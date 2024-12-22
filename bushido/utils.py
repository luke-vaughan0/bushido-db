from django.db.models import Q
import re
import ast
from django.contrib.staticfiles import finders
import collections


def nest_from_brackets(s):
    result = []
    stack = []
    current = ''
    for char in s:
        if char == '(':
            if current:
                result.append(current)
                current = ''
            stack.append(result)
            result = []
        elif char == ')':
            if current:
                result.append(current)
                current = ''
            if stack:
                popped = stack.pop()
                popped.append(result)
                result = popped
        else:
            current += char
    if current:
        result.append(current)
    return result


def recursive_split(l):
    result = []
    pattern = r'\b(AND|OR|NOT)\b'
    for item in l:
        if isinstance(item, list):
            result.append(recursive_split(item))
        else:
            split_item = re.split(pattern, item)
            result.extend([item.strip() for item in split_item if item.strip()])
    return result


def recursive_dict(l):
    result = []
    for item in l:
        if isinstance(item, list):
            result.append(recursive_dict(item))
        else:
            if "=" in item:
                thing = {}
                stuff = item.split("=")
                thing[stuff[0]] = ast.literal_eval(stuff[1])
                result.append(thing)
            else:
                result.append(item)
    return result


def create_q(l):
    result = []
    for item in l:
        if isinstance(item, list):
            result.append(create_q(item))
        else:
            if isinstance(item,dict):
                result.append(Q(**item))
            else:
                result.append(item)
    return result


def evaluate_expression(expression):
    def evaluate_sub_expression(sub_expr):
        if isinstance(sub_expr, list):
            result = evaluate_expression(sub_expr)
        else:
            result = sub_expr
        return result
    if len(expression) == 1:
        return expression[0]
    if expression[0] == "NOT":
        evaluated_expr = [~evaluate_sub_expression(expression[1])]
    else:
        evaluated_expr = [evaluate_sub_expression(expression[0])]
    for i in range(0, len(expression)):
        if i == 0 and expression[0] == "NOT":
            continue
        if isinstance(expression[i], str):
            operator = expression[i]
            operand = evaluate_sub_expression(expression[i + 1])
            if operator == "AND":
                evaluated_expr[-1] &= operand
            elif operator == "OR":
                evaluated_expr[-1] |= operand
    return evaluated_expr[0]


def q_object_from_string(string):
    result = nest_from_brackets(string)
    result = recursive_split(result)
    result = recursive_dict(result)
    result = create_q(result)
    result = evaluate_expression(result)
    return result


def queryset_from_string(query_string):
    from bushido.models import Unit
    queryset = Unit.objects.all()
    parts = query_string.split(";")
    for part in parts:
        part = part.strip()
        if not part.startswith("EXCLUDE"):
            queryset = queryset.filter(q_object_from_string(part))
        else:
            part = part.replace("EXCLUDE", "", 1).strip()
            queryset = queryset.exclude(q_object_from_string(part))
    return queryset


def get_properties(model):
    if hasattr(model, "properties"):
        results = model.properties.split(";")
    elif hasattr(model, "validation"):
        results = model.validation.split(";")
    else:
        raise AttributeError
    properties = collections.defaultdict(list)
    for item in results:
        match = re.match(r"\s*([A-Z]*) ?(.*)?", item)
        if not match.group(1):  # TODO remove this and add filter to validation
            properties["FILTER"].append(match.group(2))
        properties[match.group(1)].append(match.group(2))
    return properties


def convertToNew(theme):
    old = theme.validation
    old = old.replace("faction__shortName=\"ronin\"", "ronin_factions__shortName=\"" + theme.faction.shortName + "\"")
    old = old.split("Unit.objects.filter(")[1]
    old = old.replace(".distinct()", "")
    old = old.split(".exclude(")[0]
    old = old[:-1]
    commaSplit = old.split("), ")
    for i, item in enumerate(commaSplit):
        commaSplit[i] = item + ")"
    commaSplit[-1] = commaSplit[-1][:-1]
    old = ""
    for item in commaSplit:
        if item != commaSplit[0]:
            old += " & "
        old += "(" + item + ")"
    brackets = 0
    fullBracket = True
    for i, char in enumerate(old):
        if char == "(":
            brackets += 1
        if char == ")":
            brackets -= 1
        if brackets == 0 and i < len(old)-1:
            fullBracket = False
            break
    if fullBracket:
        old = old[1:-1]
    brackets = 0
    delete = False
    new = ""
    for i, char in enumerate(old):
        if char == "Q" and old[i+1] == "(":
            delete = True
            brackets += 1
        elif char == "(" and delete:
            delete = False
        elif char == ")" and brackets > 0:
            brackets -= 1
        elif char == "&":
            new += "AND"
        elif char == "|":
            new += "OR"
        elif char == "~":
            new += "(NOT "
            brackets -= 1
        else:
            new += char
    return new


def testTheme(theme):
    actual = eval(theme.validation)
    new = queryset_from_string(convertToNew(theme)).distinct()
    same = list(new.values_list("name", flat=True)) == list(actual.values_list("name", flat=True))
    print(theme.name + " - " + str(same))
    if not same:
        print(actual)
        print(new)
        print(set(actual).difference((set(new))))


def get_card(user=None, item=None, extra=""):
    name = item.cardName if hasattr(item, "cardName") else item.name
    class_names = {
        "Unit": "Model",
        "KiFeat": "Feat"
    }
    item_type = class_names.get(item.__class__.__name__, item.__class__.__name__).lower()+"s"
    card = 'bushido/' + item.faction.shortName + "/" + item_type + "/" + name + extra + (".jpg" if not re.match(r".*\.(jpg|png)", extra) else "")
    if not finders.find(card.replace("bushido/", "bushido/unofficial/").replace(".jpg", ".png")):
        return card
    if user and user.is_authenticated:
        if not user.userprofile.use_unofficial_cards:
            return card
    return card.replace("bushido/", "bushido/unofficial/").replace(".jpg", ".png")


def text_to_list(text):
    from bushido.models import Unit, Event, Enhancement, List, ListUnit, Theme, ListEvent
    unit_list = List()
    unit_list.save()
    themes = [theme.lower() for theme in Theme.objects.values_list("name", flat=True)]
    factions = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(":", 1)
        # remove rice, brackets and digits, non letters before the first letter, and A-F when it's not in a word
        pattern = r"\[\d+ Rice]|[\[\]()\d]|^[^a-zA-Z]+| [A-F](?![a-zA-Z])"
        name = re.sub(pattern, "", parts[0]).strip()
        print(name)

        if not unit_list.theme:
            if name.lower() in themes:
                unit_list.theme = Theme.objects.get(name=name)
                unit_list.faction = unit_list.theme.faction

        # units
        units = Unit.objects.filter(Q(name__iexact=name) | Q(cardName__iexact=name))
        if len(units) == 0:
            pass
        elif len(units) == 1:
            unit = units[0]
            factions.append(unit.faction)
            enhancements = []
            equipment = []
            if len(parts) > 1:
                for part in parts[1].split(","):
                    enhancement = Enhancement.objects.filter(name__iexact=part.strip())
                    if len(enhancement) == 1:
                        enhancement = enhancement[0]
                    elif len(enhancement) == 0:
                        continue
                    else:
                        enhancement = [x for x in enhancement if x.faction == unit.faction]
                        if len(enhancement) != 1:
                            continue
                        enhancement = enhancement[0]
                    if enhancement.isEquipment:
                        equipment.append(enhancement)
                    else:
                        enhancements.append(enhancement)
            list_unit = ListUnit(list=unit_list, unit=unit, equipment=equipment[0] if equipment else None)
            list_unit.save()
            list_unit.enhancements.set(enhancements)
            continue
        else:
            for part in parts[1].split(","):
                units = Unit.objects.filter(name__iexact=part.strip())
                for unit in units:
                    factions.append(unit.faction)
                    list_unit = ListUnit(list=unit_list, unit=unit)
                    list_unit.save()
            continue

        # events
        events = Event.objects.filter(name__iexact=name)
        if len(events) > 1:
            events = [x for x in events if x.faction == unit_list.faction]
        if len(events) != 0:
            list_event = ListEvent(list=unit_list, event=events[0])
            list_event.save()

    # guessing faction
    if not unit_list.faction and len(factions) != 0:
        guessed_faction = collections.Counter(factions).most_common(2)
        if guessed_faction[0][0].shortName != "ronin":
            guessed_faction = guessed_faction[0][0].id
        elif len(guessed_faction) > 1:
            guessed_faction = guessed_faction[1][0].id
        else:
            guessed_faction = collections.Counter(unit_list.units.values_list("ronin_factions", flat=True)).most_common(1)[0][0]
        unit_list.faction_id = guessed_faction
    unit_list.save()
    print(unit_list.__dict__)
    print(unit_list.is_list_valid())
    return unit_list


def mock_test():
    from django_mock_queries.mocks import mocked_relations
    from django_mock_queries.query import MockModel, MockSet
    from bushido.models import Unit, UnitType
    # Create mock libraries
    edo = Unit.objects.get(name="Edogawa")
    print(edo.types.all())
    #initial_types = edo.types.all()

    #unit_set = MockSet(edo)
    #type_set = MockSet(*initial_types)
    #print(list(unit_set))
    #print(list(type_set))

    with mocked_relations(UnitType):
        print("get here?")
        #print(list(Unit.objects.all()))
        extra_type = UnitType.objects.create(unit=edo, type="Testing")
        print(list(UnitType.objects.all()))
        print(extra_type)
        print(extra_type.unit)
        edo.types.add(extra_type)
        print(edo.types.all())
        test = Unit.objects.filter(types__type="Testing")
        print(list(test))
    test = Unit.objects.filter(types__type="Testing")
    print(edo.types.all())
    print(list(test))

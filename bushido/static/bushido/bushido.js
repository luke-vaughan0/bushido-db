$(document).ready( function () {
    var panes = $('.search-panes');
    var table = $('.data-table').DataTable({
        "pageLength": 100,
        "lengthMenu": [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
        dom: panes.length ? 'Plfrtip' : 'lfrtip',
        searchPanes: {
            layout: 'columns-1',
            dtOpts: {
                paging: true,
                pagingType: 'numbers',
            }
        }
    });
    if (panes.length) {
        table.searchPanes.container().prependTo(panes);
    }
    $('input[id*="-isRanged"').each(function(){
        if ($(this).prop("checked")){
            $(this).closest( ".formset-form" ).children(".range-bands").removeClass("d-none");
        }
    });
} );

$('body').on('keypress', function(keyPress) {
    var input = $('input[name="search"]');
    if(!$(':focus').length && !input.is(':focus') && keyPress.key.match(/^[0-9a-zA-Z]+$/)) {
        input.val("");
        input.trigger("focus");
    }
});


$("#DiscordShare").on("click", function() {
    navigator.clipboard.writeText($('#DiscordShareText').text());
    $("#DiscordShare").tooltip('show');
    setTimeout(function() {$('#DiscordShare').tooltip('hide')}, 2000);
});

$(".formset-container").on("change", ".formset-add", function() {
    var current_id = parseInt(this.id.split("-")[1]);
    var name_prefix = this.name.split("-")[0];
    var formset_container = $(this).closest( ".formset-container" );
    var num_forms = formset_container.children("div").length-1;
    var current_form = $(this).closest( ".formset-form" )
    var total_form_count = formset_container.children('[id*="TOTAL_FORMS"]');
    if (current_form.is(formset_container.children("div").last().prev())) {
        var new_form = formset_container.children(".empty-form").clone().insertBefore( formset_container.children(".empty-form") ).removeAttr("id").removeClass("d-none empty-form");
        new_form.find('[name*="' + name_prefix + '-"],[id*="' + name_prefix + '-"]').each(function(){
            if ($(this).attr('name')) {$(this).attr('name', $(this).attr('name').replace(/__prefix__/, num_forms));}
            if ($(this).attr('id')) {$(this).attr('id', $(this).attr('id').replace(/__prefix__/, num_forms));}
        });
        total_form_count.val(parseInt(total_form_count.val())+1);
    } else if (!this.value && !current_form.is(formset_container.children("div").last().prev())) {
    /* && current_form.is(formset_container.children("div").last().prev().prev()) */
        $(this).closest( ".formset-form" ).addClass("d-none");
        current_form.find('input[id*="DELETE"]').prop("checked", true);
    }
});

$(".formset-container").on("change", 'input[id*="-isRanged"]', function() {
    if ($(this).prop("checked")){
            $(this).closest( ".formset-form" ).children(".range-bands").removeClass("d-none");
        } else {
            $(this).closest( ".formset-form" ).children(".range-bands").addClass("d-none");
        }
});
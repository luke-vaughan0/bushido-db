$(document).ready( function () {
    var panes = $('.search-panes')
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

} );
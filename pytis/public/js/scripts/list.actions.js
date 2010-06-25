jQuery(function($){
	var tables = $('table#item-list').pytisList();	
	
	tables.bind('clickRow', function(e, row) {
        var id = getIdFromClassname($(row).attr('class'));
		
		location.href = window.pytis_urls.editRow + '/' + id;		
	});
});
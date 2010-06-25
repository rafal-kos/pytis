$(document).ready(function(){
	
	
	//$("#show-toolbar").tabs();
	//$("#bottom-toolbar").tabs();	
	
    $("li#toggle-bookmarks-listing.enabled").live("mouseover", function(){        
        $(this).children("ul").show();			        
    }).live("mouseout", function(){        
        $(this).children("ul").hide();		
    });      
	
	$(".close").click(
		function () {
			$(this).parent().fadeTo(400, 0, function () { // Links with the class "close" will close parent
				$(this).slideUp(400);
			});
			return false;
		}
	);
	
	$('fieldset.module h2').each(function(){		
		var  $header = $(this),
			$box = $(this).parent('fieldset.module'),								
			$bottom = $box.children('.bottom'), 
			$collapse = $('<span class="collapse">Collapse/Expand</span>').appendTo($header);
		
		if ($box.hasClass('hide')) {
			$collapse.toggleClass('change');
			$bottom.css({ display: 'none' });
		}
		
		$header.css({
			cursor: 'pointer'
		}).click(function(event){
			if ($(event.target).is('a')) return true;
			
			$collapse.toggleClass('change');
			$bottom.slideToggle();
		});
	});

	
});

$(document).ajaxSend(function() {
	$('#loading').show();        
});

$(document).ajaxStop(function() {
	$('#loading').hide();
});
(function($){  
	$.pytisList = {
    	default : {
      		tr : {
        		hover: 'selected',       // "hover" class for TR
        		selected: 'selected', // "selected" class
        		click: {
          			prevent:	true,   // prevent execution of click event on TR in when clicking...
          			preventOn:  'a, input, button, textarea' // on these selectors
        		}
      		},
      		td : {
        		// CSS selectors for selection checkboxes
        		check: { one: '.check:checkbox', all: '.checkAll:checkbox' }
      		},
      		batch : { trigger: 'a.batch[rel]', field: '#batch_action' }
    	}
  	};
	
	$.fn.extend({
    	pytisList : function (settings)
    	{
			settings = $.extend(true, {}, $.pytisList.default, settings);
			return this.each(function() {
				var t = $(this);
				
				if (t.is('table'))
				{					
					var tr = t.find('tbody tr');
					var gc = t.find(settings.td.check.all);
					var ic = tr.find(settings.td.check.one);
					
					// hover
          			if (settings.tr.hover)
          			{
            			tr.live('mouseover', function() { $(this).addClass(settings.tr.hover); });
            			tr.live('mouseout', function() { $(this).removeClass(settings.tr.hover); });					
          			}
					
					// click
					//tr.live('click', function(e) { if (!e.isImmediatePropagationStopped()) t.trigger('clickRow', $(this)); });
					
					// select one
          			ic.live('click', function(e) {
	            		var parent = $($(this).parents('tr').get(0)), all, sel;
	            
	            		if (this.checked) {
	              			parent.addClass(settings.tr.selected);
	              			t.trigger('selectRow', [parent.get()]);
	            		} else {
	              			parent.removeClass(settings.tr.selected);
	              			t.trigger('unselectRow', [parent.get()]);
	            		}
	            
	            		sel  = ic.filter(':checked').length;
	            		all  = (ic.filter(':checked').length == ic.length);
	            		gc.attr('checked', (all ? 'checked' : ''));
	            
	            		if (all) {
	              			t.trigger('selectAll', [tr]);
	            		} else if (sel == 0) {
	              			t.trigger('unselectAll', [tr]);
	            		}
          			});
					
					// select all (global check)
          			gc.bind('click', function(e) {
            			var all  = t.find(settings.td.check.one).attr('checked', this.checked),
                		rows = all.parents('tr'),
                		evt;
            
            			if (this.checked) {
              				rows.addClass(settings.tr.selected);
              				t.trigger('selectAll', [tr]);
            			} else {
              				rows.removeClass(settings.tr.selected);
              				t.trigger('unselectAll', [tr]);
            			}
          			});
          
          			if (settings.tr.click.prevent) {
            			//tr.find(settings.tr.click.preventOn).live('click', function(e) { e.stopImmediatePropagation(); });
          			}
          
          			// batch actions
          			t.find(settings.batch.trigger).click(function(){ var rel = $(this).attr('rel'); t.trigger(rel, [t]).trigger('Batch', [t, rel]); });
				}
			});
		}
	});

})(jQuery);

var $rows = {}
$rows.get = function($rowElement) {
    return $rows[$rowElement.attr('id')];
}


function InvoicePosition($positionRow){	
	this.element = $positionRow;	
	$rows[$id = $positionRow.attr('id')] = this;
	
	$positionRow.find('.delete').bind('click', function(event){
		$(this).parent().parent().remove();
	})
	
	this.bindChange($id);
}

InvoicePosition.prototype.bindChange = function($id){	
	this.element.find('input,select').each(function() {
        if ($(this).is('.brutto_value')) {
            $(this).bind('change', {}, $rows[$id].changeBrutto);
        } else {
            $(this).bind('change', {}, $rows[$id].change);			
        }
    });
}

InvoicePosition.prototype.setValue = function($key, $value) {
    $obj = this.element.find('.' + $key);
    
    // aktualizowanie podsumowania aktualnej pozycji
    if ($obj.is('input')) {
        $obj.val($value.currency());
    } else {
        $obj.empty();
        $obj.text($value.currency());
    }
};

InvoicePosition.prototype.getValue = function($key) {
	$object = this.element.find('.' + $key);
	
    $value = $object.is('input,select') ? $object.val() : $object.text();
    
    return $value != undefined && !isNaN($value = $value.replace('%', '').float()) ? $value : 0;
};

InvoicePosition.prototype.change = function() {
	$row = $(this).is('input,select') ? $rows[$(this).parents('tr:eq(0)').attr('id')] : this;
	
	var netto_value = $row.getValue('netto_value');
	var tax_type = $row.getValue('tax_type option:selected');
	
	var tax_value = netto_value * tax_type / 100;
	var brutto_value = netto_value + tax_value;
	
	$row.setValue('tax_value', tax_value);
	$row.setValue('brutto_value', brutto_value);
	$row.setValue('netto_value', netto_value);
}

InvoicePosition.prototype.changeBrutto = function(){
	$row = $(this).is('input,select') ? $rows[$(this).parents('tr:eq(0)').attr('id')] : this;
	
	var brutto_value = $row.getValue('brutto_value');
	var tax_type = $row.getValue('tax_type');
	
	var netto_value = brutto_value /  (1 + tax_type / 100);
	var tax_value = netto_value * tax_type / 100;			
	
	$row.setValue('tax_value', tax_value);
	$row.setValue('netto_value', netto_value);
	$row.setValue('brutto_value', brutto_value);	
}

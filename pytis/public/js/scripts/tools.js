/*
Looks for a value matching <string>-<integer>, like in "invoice-74"
and gets the numerical part (74).
*/
function getIdFromClassname(classname)
{
	var id = classname.match(/-(\d+)/).pop();
	if (isNaN(id))
	{
    	throw "I can't get a numerical id from '" + classname + "' class value.";
  	}
  	return id;
}

function currencyFormat($value) {
    return ($value.toFixed(2)+"").replace(',','.');
}

String.prototype.float = function() {
    return parseFloat(this.replace(',','.').replace(/ /g,''));
}

String.prototype.currency = function() {
    return (this.float().toFixed(2)+"").replace(',','.');
}

Number.prototype.currency = function() {
    return (this.toFixed(2)+"").replace(',','.');
}

Number.prototype.pad = function($char, $length) {
    return (this + "").pad($char, $length);
}

String.prototype.pad = function($char, $length) {
    var $result = this;
    
    while ($result.length < $length) {
        $result = $char + $result;
    }
    
    return $result;
}

function getObjectValue($object)
{   
    $value = $object.is('input,select') ? $object.val() : $object.text();
    
    return $value != undefined && !isNaN($value = $value.replace('%', '').float()) ? $value : 0;
}


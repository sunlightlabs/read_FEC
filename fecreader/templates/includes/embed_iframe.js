{% load staticfiles %}

<!-- start js inpage include -->
<!-- ui-dialog -->
<div id="dialog" title="Embed this chart">
  <!-- crazy workaround: http://stackoverflow.com/a/10455573 -->
  <span class="ui-helper-hidden-accessible"><input type="text"/></span>
  <!-- end nutty workaround -->
  <div class="dialog-body"><span id="modal_body" style="font-size: 12px;">
  You can embed this chart on your site with this code snippet:<br>
  <div style="width: 350px; margin:10px;">
  &lt;iframe src="http:/realtime.influenceexplorer.com{{ request.get_full_path }}" {% ifequal blog_or_feature 'blog' %} width="660"{% else %} width="880"{% endifequal %}  height="520" frameborder="0" scrolling="no"&gt; &lt;/iframe&gt; 
  </div>
  <br>See the <a href="http://realtime.influenceexplorer.com/charts/" target="_none">charts page</a> for more options.
  <span id="confirmation_buttons">
  <br><br><button id="dismiss_button" class="textBtn">Ok</button></div>
  </span>
  <div id="download_div"></div>
</div>

<script src="http://realtime.influenceexplorer.com/static/dryrub/js/jquery-1.10.2.min.js"></script>
<script src="{% static 'realtimefec/js/jquery-ui-1.10.3.custom.min.js' %}"></script>

<script type="text/javascript">


$( document ).ready(function() {	
	$( "#dismiss_button" ).button();
	

	
	$( "#dismiss_button" ).click(function( event ) {
		$( "#dialog" ).dialog( "close" );
	});
	
	
	$( "#dialog" ).dialog({
		autoOpen: false,
		width: 400
	});

	// Link to open the dialog
	$( "#dialog-link" ).click(function( event ) {        
		$( "#dialog" ).dialog( "open" );
		event.preventDefault();
		
	});
});

</script>
<!-- end js include -->
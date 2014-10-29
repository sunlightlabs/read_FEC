{% load staticfiles %}

<!-- start js inpage include -->
<!-- ui-dialog -->
<div id="dialog" title="Embed this chart">
  <!-- crazy workaround: http://stackoverflow.com/a/10455573 -->
  <span class="ui-helper-hidden-accessible"><input type="text"/></span>
  <!-- end nutty workaround -->
  <div class="dialog-body"><span id="modal_body" style="font-size: 12px;">
  Select an external width for the chart <select name="embed_width" id="embed_width_chosen">
         <option value='narrow' {% ifequal blog_or_feature 'narrow' %}selected{% endifequal %}>590px</option>
         <option value='blog' {% ifequal blog_or_feature 'blog' %}selected{% endifequal %}>660 px</option>
         <option value='feature' {% ifequal blog_or_feature 'feature' %}selected{% endifequal %}>880 px</option>
     </select>
  <br>
  You can embed this chart on your site with this code snippet:<br>
  <div style="width: 350px; margin:10px;">
  &lt;iframe src="http://realtime.influenceexplorer.com<span id='full_path'>{{ request.get_full_path }}</span>" {% ifequal blog_or_feature 'blog' %} width="<span id='thiswidth'>660</span>"{% else %}{% ifequal blog_or_feature 'narrow' %} width="<span id='thiswidth'>590</span>"{% else %} width="<span id='thiswidth'>880</span>"{% endifequal %}{% endifequal %}  height="520" frameborder="0" scrolling="no"&gt; &lt;/iframe&gt; 
  </div>
  <br>For more options, see the <a href="http://realtime.influenceexplorer.com/charts/" target="_none">charts page</a>.
  <span id="confirmation_buttons">
  <br><br><button id="dismiss_button" class="textBtn">Ok</button></div>
  </span>
  <div id="download_div"></div>
</div>

<script src="http://realtime.influenceexplorer.com/static/dryrub/js/jquery-1.10.2.min.js"></script>
<script src="{% static 'realtimefec/js/jquery-ui-1.10.3.custom.min.js' %}"></script>

<script type="text/javascript">
function set_value(width_arg) {
    var path = full_path;
    if (width_arg=='blog') 
    {
        $( "#thiswidth" ).html('660');
        path = path.replace(initial_state, 'blog')
        $( "#full_path" ).html(path);
    }
    if (width_arg=='narrow') 
    {
        $( "#thiswidth" ).html('590');
        path = path.replace(initial_state, 'narrow')
        $( "#full_path" ).html(path);
    }
    if (width_arg=='feature') 
    {
        $( "#thiswidth" ).html('880');
        path = path.replace(initial_state, 'feature')
        $( "#full_path" ).html(path);
    }
    
}
var initial_state = '{{ blog_or_feature }}';
var full_path = '{{ request.get_full_path }}';
$( document ).ready(function() {	
    
    
    //<select name="embed_width" id="embed_width_chosen">
	$( "#embed_width_chosen" ).change(function( event ) {
	    set_value(this.value);    
    });
    set_value('{{ blog_or_feature }}');

    //var initial{{ blog_or_feature }}
    
    
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
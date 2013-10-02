{% load staticfiles %}
{# assumes that 'realtimefec/css/custom-theme/jquery-ui-1.10.3.custom.css' is included at the top #}

<!-- start js inpage include -->
<!-- ui-dialog -->
<div id="dialog" title="Confirm Bulk File Download">
  <!-- crazy workaround: http://stackoverflow.com/a/10455573 -->
  <span class="ui-helper-hidden-accessible"><input type="text"/></span>
  <!-- end nutty workaround -->
  <div class="dialog-body"><span id="modal_body">
  You're about to download a .csv file of itemized Federal Election Commission data. Some files may be quite large. Are you sure you want to continue?</span>
  <span id="confirmation_buttons">
  <br><br><button id="confirm_button" class="textBtn">Yes, Continue</button>&nbsp;<button id="dismiss_button" class="textBtn">No, Quit</button></div>
  </span>
  <div id="download_div"></div>
</div>

<script src="{% static 'realtimefec/js/jquery-ui-1.10.3.custom.min.js' %}"></script>
<script type="text/javascript">


	
	$( "#confirm_button" ).button();
	$( "#dismiss_button" ).button();
	
	
	
	$( "#confirm_button" ).click(function( event ) {
		alert("download confirmed");
	});

	
	$( "#dismiss_button" ).click(function( event ) {
		$( "#dialog" ).dialog( "close" );
	});
	
	
	$( "#dialog" ).dialog({
		autoOpen: false,
		width: 600,
	});

	// Link to open the dialog
	$( "#dialog-link" ).click(function( event ) {
		$( "#dialog" ).dialog( "open" );
		event.preventDefault();
	});


  function set_modal_body(sked, source) {
    data_type = ""
    if (sked.toUpperCase()=='A') {
      data_type = "contributions itemized";
    } else if (sked.toUpperCase()=='B') {
      data_type = "disbursements itemized";
    } else if (sked.toUpperCase()=='E') {
      data_type = "independent expenditures itemized"
    }
    
    string = "You're about to download a .csv file of " + data_type + source + ". You can find data dictionaries and more<a href='/about/#data_dictionaries' target='null' class='link'> in the data dictionaries section of the about page</a>.<br><br>Some files may be quite large. Are you sure you want to continue?";
    
    $('#modal_body').html(string);
  }
  
  function load_iframe(url) {
    console.log("loading iframe");
    iframe_html = '<iframe width="500" scrolling="no" height="100" frameborder="0" src="' + url + '" seamless="seamless">';
    $('#download_div').html(iframe_html)
    $('#confirmation_buttons').hide();
    $('#modal_body').hide();    
  }
  
  function reset_window() {
    $('#confirmation_buttons').show();
    $('#download_div').html('');
    $('#modal_body').show();    
    
  }
  
  function download_filing_data(filing_number, sked) {
    $('#confirm_button').unbind('click');
    $('#confirm_button').on('click', function() {
      url = "/download/filing/" + filing_number + "/" + sked + "/";
      load_iframe(url);
    });
    reset_window();
    set_modal_body(sked, " on electronic filing " + filing_number);
    $( "#dialog" ).dialog( "open" );
    
  }
  
  function download_committee_data(committee_id, sked, committee_name) {
    $('#confirm_button').unbind('click');
    $('#confirm_button').on('click', function() {
      url = "/download/committee/" + committee_id + "/"+ sked + "/";
      load_iframe(url);
    });
    reset_window();
    set_modal_body(sked, " by " + committee_name );
    $( "#dialog" ).dialog( "open" );
  }

  function download_candidate_data(candidate_id, sked, candidate_name, detailed_office) {
    $('#confirm_button').unbind('click');
    $('#confirm_button').on('click', function() {
      url = "/download/candidate/" + candidate_id + "/"+ sked + "/";
      load_iframe(url);
    });
    reset_window();
    set_modal_body(sked, " by campaign committees authorized by " + candidate_name + " in the race for " + detailed_office);
    $( "#dialog" ).dialog( "open" );
  }

</script>
<!-- end js include -->
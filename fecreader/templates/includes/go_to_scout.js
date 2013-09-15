
<!-- ui-dialog -->
<div id="confirm" title="Sign up for notifications">
  <span class="ui-helper-hidden-accessible"><input type="text"/></span>
  <div class="dialog-body"><span id="modal_body">You're being sent to <a class="link" href="https://scout.sunlightfoundation.com/">Scout</a>, Sunlight's notification tool, to receive alerts whenever <span id="filer_type">this committee</span> files new campaign finance reports<span id="ie_extra"></span>. If you don't have an account with Scout you'll be prompted to create one.<br><br>You can also create more complex feeds at our <a href="/alerts/" class="link">alerts page.</a></span>
  </div>
</div>
<script type="text/javascript">
  var committee_id;
  var committees_id;
  var race_feed_url;
  var is_multi_candidate = false;
  var is_race = false;
  var feedurl;
  
  function goto_scout() {
    if (is_multi_candidate) {
        feedurl = "http://realtime.influenceexplorer.com/feeds/committees/" + committees_id + "/";
    } else if (is_race) {
        feedurl = "http://realtime.influenceexplorer.com" + race_feed_url ;
        
    }else {
        feedurl = "http://realtime.influenceexplorer.com/feeds/committee/" + committee_id + "/";
    }
  	scouturl = "http://scout.sunlightfoundation.com/import/feed?url=" + encodeURIComponent(feedurl);
  	window.location = scouturl;
  	return false;
  }
  
  
  $(document).ready(function () {
    
    $( "#confirm" ).dialog({
  		autoOpen: false,
  		width: 400,
    	buttons: [
    		{
    			text: "Ok",
    			click: function() {
    				goto_scout();
    			}
    		},
    		{
    			text: "Cancel",
    			click: function() {
    				$( this ).dialog( "close" );
    			}
    		}
    	]
  	});
  });
  
  function submit_gotoscout_candidates(com_id_list) {
    committees_id = com_id_list;
    is_multi_candidate = true;
    $("#filer_type").html( "this candidate" );
    $( "#confirm" ).dialog( "open" );
  }
  
  function submit_gotoscout_race(feed_url) {
    race_feed_url = feed_url;
    is_race = true;
    $("#filer_type").html( "any candidate in this race" );
    $("#ie_extra").html(" or is targeted by an independent expenditure")
    $( "#confirm" ).dialog( "open" );
  }
  
  function submit_gotoscout(com_id) {
    committee_id = com_id;
  	$( "#confirm" ).dialog( "open" );
  }
  
</script>
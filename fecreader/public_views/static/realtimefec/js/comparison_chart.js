var partisan_colors = window.partisan_colors;
var blog_or_feature = window.blog_or_feature;
var data_series_to_choose = window.race_id_array;
var start_month = 5 
var start_day = 1
var start_year = 2014
var startDate = Date.UTC(start_year, start_month, start_day, 5, 43, 0);




// make the styles we load accessible everywhere;
var styles;

var unhighlighted = d3.rgb("#9999bb");
var highlighted = d3.rgb("#000000");


var circle_radius = 3;
// Parameters for top-level sizing of plot
var desired_height = 350;
var div_selector = "#line-chart";
// If there are too many items the legend won't fit

// list of colors
var available_colors = ['yellows', 'teals', 'reds', 'pinks', 'mints', 'magentas', 'oranges', 'blues', 'cyans', 'greens'];
var num_colors = 8;
var colors = [];

var drawLegend = true;

var tooltipwidth  = 80;
var tooltipheight = 20;

var expanded_tooltipwidth = 170;
var expanded_tooltipheight = 60;

var tooltipoffset_x = 10;
var tooltipoffset_y = 10; 

var tooltip_is_shrunk = true;

var base_width = 950;
if (blog_or_feature == 'blog') {
    base_width = 720
}
var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = base_width - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var num_colors = data_series_to_choose.length;


var data_series = [];
var week_end_dates = [];

var yFormatter = d3.format(",.0$");


var parseDate = d3.time.format("%m/%d/%Y").parse;

function fix_date(element, index, array) {
    array[index] = parseDate(element);
}

function null_or_float(string_input) {
    result = parseFloat(string_input);
    if (isNaN(result)) {
        result = 0;
    }
    return result;
}

function get_x_offset(x) {
    current_tooltipwidth = tooltipwidth;
    if (tooltip_is_shrunk) {
        current_tooltipwidth = tooltipwidth;
    } else {
        current_tooltipwidth = expanded_tooltipwidth;        
    }
    
	if (x >  width - current_tooltipwidth - 20) {
		return x - current_tooltipwidth -10 ;
	} else {
		return x + 20  ;
		}
	}

function get_y_offset(y) {
	if (y <  tooltipheight ) {
		return y + tooltipheight;
	} else {
		return y - tooltipheight;
		}
	}

function expand_tooltip() {
    d3.select(".tooltip")
        .style("width", expanded_tooltipwidth + "px")
        .style("height", expanded_tooltipheight + "px");
        tooltip_is_shrunk = false;
}

function shrink_tooltip() {
    d3.select(".tooltip")
        .style("width", tooltipwidth + "px")
        .style("height", tooltipheight + "px");
        tooltip_is_shrunk = true;
}


function roundwCommas(nStr) {
    nStr = Math.round(nStr);
    nStr += '';
    x1 = nStr;
    //x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    return x1;
}

var tooltipdiv = d3.select("body").append("div")   
    .attr("class", "tooltip")               
    .style("opacity", 0)
    .style("width", tooltipwidth + "px")
    .style("height", tooltipheight + "px");


function format_data_series(data_array, date_array, id, index) {
    // reformat an array of values to a dict with the corresponding date value
    var formatted_data = [];
    for (var i=0; i<data_array.length;i++) {
        if (date_array[i] > startDate) {
        formatted_data.push({'value':data_array[i], 'date':date_array[i], 'id':id, 'index':index})
        }
    }
    return formatted_data;
}

function read_data(text) {
    rows = d3.csv.parseRows(text);
    header_row = rows[0];
    var num_cols = header_row.length;
    week_end_dates = header_row.slice(2,num_cols)    
    week_end_dates.forEach(fix_date);
    
    data_rows = rows.slice(1,rows.length);
    
    console.log("data series is: " + data_series_to_choose);
    // just pull out the rows we care about
    for (var i=0; i<data_series_to_choose.length; i++) { 
            console.log("i is: " + i + " and data series is: " + data_series_to_choose[i]);
            console.log("Adding data series: " + data_rows[data_series_to_choose[i]][1]);
            data_series.push( {'id':data_rows[data_series_to_choose[i]][0], 'name':data_rows[data_series_to_choose[i]][1], 'data':format_data_series(data_rows[data_series_to_choose[i]].slice(2,num_cols), week_end_dates, data_rows[data_series_to_choose[i]][0], i )} );
    };
    
    console.log(data_series);
    console.log(" length is: " + data_series.length);
    
    var svg = d3.select(div_selector+' svg');
    var chart = d3.select(".chart-area");
    
    if (partisan_colors) {
        colors[1] = styles.colors.data.parties.republican.hex;
        colors[0] = styles.colors.data.parties.democrat.hex;
    } else {
        for (var i=0; i<num_colors; i++) {
            colors[i] = styles.colors.network_graph[available_colors[i]][0].hex;
        }
    }
    
     // hash the colors
    var color_dict = {}
    var color_index = 0;
    for (var key in data_series ) {
        console.log("adding key: " + key);
        color_dict[data_series[key]['id']] = colors[color_index++];
    }
    console.log(color_dict);
    
    

 //  ... get default margins from specs
    var margin = styles.plot_elements.canvas.margin;

    //  ... create invisible text object
    var testText = svg.append("g")
                    .append("text")
                      .classed("test-text", "true")
                      .classed("axis", "true")
                      .text(function(d){ return "XXXX" });

    var longestLabel = testText[0][0].getBBox().width
    //  ... measure width of invisible text object
    var yLabelWidth = Math.max(longestLabel,0)

    testText.data([]).exit().remove();

    //  ... use larger of two margins
    var suggestedLeftMargin = yLabelWidth + parseInt(styles.text_styles.axis_title['font-size']) + styles.plot_elements.axis.title_padding;

    margin.left = Math.max(margin.left, suggestedLeftMargin);

    //  ... follow D3 margin convention as normal
    var width = styles.plot_elements.canvas.width[blog_or_feature] - margin.left - margin.right,
        height = desired_height - margin.top - margin.bottom;

    svg.attr("width", width + margin.left + margin.right)
       .attr("height", height + margin.top + margin.bottom);
    
   var x = d3.time.scale()
           .range([0, width]);

   var y = d3.scale.linear()
           .range([height, 0]);

           // chart-area
  chart.on("mousemove", function(){
    coordinates = d3.mouse(this);
    var x = d3.event.pageX;
    var y = d3.event.pageY;

    xwindow =  get_x_offset(x);
    ywindow =  get_y_offset(y);
    tooltipdiv.style("left", xwindow + "px")     
              .style("top", ywindow + "px")
    }) ;

   // get max values
   
   var minDate = d3.min(data_series, function(series) { return d3.min(series['data'], function(datum) { return (datum['date'])
       })
   });

   var maxDate = d3.max(data_series, function(series) { return d3.max(series['data'], function(datum) { return (datum['date'])
       })
   });
   
   var maxValue = d3.max(data_series, function(series) { return d3.max(series['data'], function(datum) { return null_or_float(datum['value'])
       })
   });
   
   // Add day at the end
   var displayendDate = new Date();
   displayendDate.setDate(maxDate.getDate() + 1); 
   
   
   
   x.domain([minDate, displayendDate]);            
   y.domain([0, maxValue + 1000000]);
   
   /*
    * Creating Axes and Gridlines (innerTick)
    */
   var xAxis = d3.svg.axis()
       .ticks(5)
       .scale(x)
       .innerTickSize(-height) // really long ticks become gridlines
       .outerTickSize(0)
       .tickPadding(5)
       .orient("bottom");

   var yAxis = d3.svg.axis()
       .scale(y)
       .orient("left")
       .innerTickSize(-width) // really long ticks become gridlines
       .outerTickSize(0)
       .tickPadding(5)
       .tickFormat(function(d){ return "$"+yFormatter(d/1000000) +"M";});
   

   /*
    * Drawing chart
    */
   var lineChart = svg.append("g")
       .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

   //  ... add x axis
   lineChart.append("g")
       .attr("class", "x axis")
       .attr("transform", "translate(0," + height + ")")
       .call(xAxis)
     .append("text")
       .classed("title",true)
       .attr("x", function() { return (width / 2.0);}) // anchors title in middle of chart
       .attr("y", function() { return (margin.bottom);})
       .style("text-anchor", "middle") // centers title around anchor
       .text("");
       
       //////
       // Hacky way to draw a legend. These dimensions should get pushed to styles.json. 
       // This should accomodate up to three house races, but not break if there are one or two. 
       // This will just keep drawing to the right if more races are present. 
       // If more space is needed could push the legendx smaller
       /////
       
       if (drawLegend) {
       
           var legendx = 90;
           var legendy = 335;
           var legend_width = 360;
           var legend_height = 80;
       
           var legend_inner_padding = 3;
           var sample_line_voffset = 5;
           var sample_line_length = 20;
           var text_x_offset = 3;

           // We draw left to right. Track where we are here
           var xcursor_position = legendx;
           //var ycursor_position = legendy;
           
           // This could be set dynamically, but... 
           var num_items = 3;
       
           for (var key in data_series ) {
       
           //for (var i = 0; i < num_items; i++) {
           
               var this_color = color_dict[data_series[key]['id']];
               // data_series color_dict[data_series[key]['id']] 
               var this_name = data_series[key]['name'];
           
               xcursor_position += legend_inner_padding;
               var x_start = xcursor_position;
           
               // draw the sample line
               svg.append("line")
                   .attr("x1", x_start)
                   .attr("y1", legendy + sample_line_voffset)
                   .attr("x2", x_start + sample_line_length)
                   .attr("y2", legendy + sample_line_voffset)
                   .attr("stroke-width", 3)
                   .attr("stroke", this_color);
               
               // and the sample dot
               var circle = svg.append("circle")
                   .attr("cx", x_start + sample_line_length/2)
                   .attr("cy", legendy + sample_line_voffset)
                   .attr("r", circle_radius)
                   .style("fill", this_color);
           
               // Add line length and text offset. 
               xcursor_position += sample_line_length + text_x_offset; 
               
               var text = svg.append("text")
                       .attr("x", xcursor_position)
                       .attr("y", legendy + sample_line_voffset)
                       .attr("dy", 4)
                       .style("fill", styles.text_styles.point_label.color)
                       .style("font-family", styles.text_styles.point_label['font-family'])
                       .style("font-size", "16px")
                       .text(this_name);
               
               // Add text width
               var textwidth = Math.ceil(text[0][0].getBBox().width);
               xcursor_position += textwidth;
               
           }
       }


   //  ... add y axis with value labels
    lineChart.append("g")
        .attr("class", "y axis")
        .call(yAxis)
      .append("text")
        .classed("title",true)
        .attr("transform", "rotate(-90)")
        .attr("x", function() { return -(height / 2.0);})
        .attr("y", function() { return -(margin.left - styles.plot_elements.axis.label_padding);})
        .attr("dy", function() { return styles.text_styles.axis_label['font-size']; })
        .style("text-anchor", "middle")
        .text("Total independent expenditures reported");


    // line drawing function
    var line = d3.svg.line()
        //.interpolate("basis")
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.value); });
    
    var chart_data = lineChart.selectAll(".party")
        .data(data_series)
      .enter().append("g")
        .attr("class", "party");

    
    
    chart_data.append("path")
        .attr("class", "line")
        .attr("d", function(d) { return line(d.data); })
        .style("stroke-width", 4)
        .style("fill", "none")
        .style("stroke", function(d) {  return color_dict[d['id']] });


    var point = chart_data.append("g")
        .attr("class", "line-point");

    point.selectAll("circle")
        .data(function(d,i){ return d.data; })
      .enter().append("circle")
        .attr("cx", function(d) { return x(d.date); })
        .attr("cy", function(d) { return y(d.value); })
        .attr("r", circle_radius)
        .attr("date", function(d) { return d.date; })
        .attr("value", function(d) { return d.value; })
        .attr("id", function(d) { return d.id; })
        .attr("index", function(d) { return d.index; })
        .attr("defaultfill", function(d) {  return color_dict[d['id']]; })
        .style("fill", function(d) {  return color_dict[d['id']]; })

        .on("mouseover", function(f,g){
          d3.select(this).attr("r", 5);
          expand_tooltip();
          month = f.date.getMonth() + 1;
          day = f.date.getUTCDate();
          var thistext = "Week ending: " + month + "/" + day + "<br>Total spent: $" + roundwCommas(f.value); 
          tooltipdiv.style("opacity",1);
          console.log("mouseover: " + f.index);
          tooltipdiv.html( "<b>" + data_series[f.index]['name'] + "</b> <br>" + thistext);            
          })
          
          .on("mouseout", function(){
          d3.select(this).attr("r", circle_radius);
          tooltipdiv.style("opacity",0);
            
          })
        

    
}

d3.json(window.jsonURL, function(error, s) {

        styles = s;

        // grab the data as text, we'll parse the rows out later
        d3.text("/static/data/weekly_ies.csv", read_data);
        // realtime.influenceexplorer.com/static/data/weekly_ies.csv
        //
});
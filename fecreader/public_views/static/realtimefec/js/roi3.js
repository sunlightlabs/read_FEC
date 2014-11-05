// make the styles we load accessible everywhere;
var styles;

var unhighlighted = d3.rgb("#9999bb");
var unhighlighted_opacity = 0.5;
var highlighted = d3.rgb("#000000");

var tooltipwidth  = 80;
var tooltipheight = 20;

var expanded_tooltipwidth = 190;
var expanded_tooltipheight = 90;

var tooltipoffset_x = 10;
var tooltipoffset_y = 10; 

var tooltip_is_shrunk = true;

var circle_radius = 3;
// Parameters for top-level sizing of plot
var blog_or_feature = window.blog_or_feature;
var desired_height = 350;
var div_selector = "#line-chart";


var max_spending = 70000000;
var max_circle_size = 25;

var rows_to_read = 50;


var data_series = [];

var yFormatter = d3.format(",.0$");

var parseDate = d3.time.format("%m/%d/%Y").parse;

var base_width = 950;
if (blog_or_feature == 'blog') {
    base_width = 720
}
if (blog_or_feature == 'narrow') {
    base_width = 650
}
var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = base_width - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;
    



var r_color;
var d_color;
var i_color;


function get_x_offset(x) {
    current_tooltipwidth = tooltipwidth;
    if (tooltip_is_shrunk) {
        current_tooltipwidth = tooltipwidth;
    } else {
        current_tooltipwidth = expanded_tooltipwidth;        
    }
    
	if (x >  width - current_tooltipwidth - 20) {
		return x - current_tooltipwidth -20 ;
	} else {
		return x + 20  ;
		}
	}

function get_y_offset(y) {
    
    current_tooltipheight = tooltipheight;
    if (tooltip_is_shrunk) {
        current_tooltipheight = tooltipheight;
    } else {
        current_tooltipheight = expanded_tooltipheight;        
    }
    
	if (y <  current_tooltipheight ) {
		return y + current_tooltipheight;
	} else {
		return y - current_tooltipheight;
		}
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
    
d3.selection.prototype.moveToFront = function() {
  return this.each(function(){
    this.parentNode.appendChild(this);
  });
};

var tooltipdiv = d3.select("body").append("div")   
    .attr("class", "tooltip")               
    .style("opacity", 0)
    .style("width", tooltipwidth + "px")
    .style("height", tooltipheight + "px");

function fix_date(element, index, array) {
    array[index] = parseDate(element);
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

function null_or_float(string_input) {
    result = parseFloat(string_input);
    if (isNaN(result)) {
        result = 0;
    }
    return result;
}

function get_fill_color(d) {
    if (d.political_leaning == 'D') {
        return d_color;
    }
    if (d.political_leaning == 'R') {
        return r_color;
    }
    return i_color;

}


var circle_scale = d3.scale.sqrt().domain([ 0, max_spending ]).range([ 1, max_circle_size ]);

function read_data(text) {
    rows = d3.csv.parseRows(text);
    header_row = rows[1];
    var num_cols = header_row.length;

    
    data_rows = rows.slice(2,rows.length);
    
    // just pull out the rows we care about
    for (var i=0; i<rows_to_read; i++) { 
            var this_line = {'fec_id':data_rows[i][0], 'name':data_rows[i][1], 'political_leaning':data_rows[i][5], 'roi':100*parseFloat(data_rows[i][7]), 'support_winners':parseFloat(data_rows[i][8]),'oppose_losers':parseFloat(data_rows[i][9]), 'support_losers':parseFloat(data_rows[i][10]), 'oppose_winners':parseFloat(data_rows[i][11]), 'support_unclassified':parseFloat(data_rows[i][12]), 'oppose_unclassified':parseFloat(data_rows[i][13]) };
            this_line['total_positive'] = this_line['support_winners'] + this_line['support_losers'] + this_line['support_unclassified'];
            this_line['total_negative'] = this_line['oppose_winners'] + this_line['oppose_losers'] + this_line['oppose_unclassified'];
            this_line['total_spending'] = this_line['total_positive'] + this_line['total_negative'];
            this_line['fraction_positive'] = 100.0*(0.0+this_line['total_positive'])/(0.0+this_line['total_spending'])
            
            
            if (isNaN(this_line['roi'])) {
                this_line['roi'] = 0.0;
            }
            if (this_line['name'].indexOf("SEIU") > -1) {
                this_line['name'] = "SERVICE EMPLOYEES INTERNATIONAL UNION";
            } else if (this_line['name'].indexOf("AMERICAN FEDERATION OF STATE") > -1) {
                this_line['name'] ="AMERICAN FEDERATION OF STATE COUNTY & MUNICIPAL EMPLOYEES"
            }
            
            data_series.push( this_line);
    };
    
    var svg = d3.select(div_selector+' svg');
    var chart = d3.select(".chart-area");
    


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


   var x = d3.scale.linear()
           .range([0, width]);

   var y = d3.scale.linear()
           .range([height, 0]);
   
   
   x.domain([-5, 105]);            
   y.domain([-5, 105]);
   
   /*
    * Creating Axes and Gridlines (innerTick)
    */
   var xAxis = d3.svg.axis()
       .ticks(5)
       .scale(x)
       .innerTickSize(-height) // really long ticks become gridlines
       .outerTickSize(0)
       .tickPadding(5)
       .tickFormat(function(d){ return d + "%"})
       .orient("bottom");

   var yAxis = d3.svg.axis()
        .ticks(5)
       .scale(y)
       .orient("left")
       .innerTickSize(-width) // really long ticks become gridlines
       .outerTickSize(0)
       .tickPadding(5)
       .tickFormat(function(d){ return d + "%"});
   

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
       // subtract a few pixels so bottom of letters aren't cut off
       .attr("y", function() { return (margin.bottom - 3);})
       .style("text-anchor", "middle") // centers title around anchor
       .text("Return on investment for general election independent expenditures");

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
        .text("Fraction of general election spending positive");







    lineChart.selectAll("circle")
        .data(data_series)
      .enter().append("circle")
        .attr("cx", function(d) { return x(d.roi); })
        .attr("cy", function(d) { return y(d.fraction_positive); })
        .attr("r", function(d) { return circle_scale(d.total_spending) })
        .attr("name", function(d) { return d.name; })
        .attr("fill", function(d) { return get_fill_color(d); })
        .attr("stroke", "white")
        .attr("stroke-width", 1)
        

        
        .on("mouseover", function(f,g){
          d3.select(this).attr("stroke", "black").attr("stroke-width", 2);
          var thistext = '<div><h4>' + f.name + "</h4><dl><dt>Return on investment:</dt><dd> " + roundwCommas(f.roi) + "%</dd><dt>Positive spending:</dt><dd>" + roundwCommas(f.fraction_positive) + "%</dd><dt>Total spending:</dt><dd> $" + roundwCommas(f.total_spending) + "</dd></dl></div>"
          tooltipdiv.style("opacity",1);
            tooltipdiv.html( thistext);
            expand_tooltip();
            
          })
          .on("mouseout", function(){
          d3.select(this).attr("stroke", "white").attr("stroke-width", 1);
          tooltipdiv.style("opacity",0);
          shrink_tooltip();
            
          })

          

    
}

d3.json(window.jsonURL, function(error, s) {

        styles = s;
        
        // Styles are too faint
        r_color = styles.colors.data.parties.republican.hex;
        d_color = styles.colors.data.parties.democrat.hex;
        //r_color = "#FF0000";
        //d_color = "#0000FF";
        i_color = styles.colors.network_graph['mints'][0].hex;

        // grab the data as text, we'll parse the rows out later
        //d3.text("/static/data/roi.csv", read_data);
        d3.text("/static/realtimefec/js/roi.csv", read_data);
        
        

});
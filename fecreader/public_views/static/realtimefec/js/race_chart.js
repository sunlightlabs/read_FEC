
function null_or_float(string_input) {
    result = parseFloat(string_input);
    if (isNaN(result)) {
        result = 0;
    }
    return result;
}

function compare(a,b) {
  if (a.cycle_week_number < b.cycle_week_number)
     return -1;
  if (a.cycle_week_number > b.cycle_week_number)
    return 1;
  return 0;
}


// local development path
// d3.json('../static/realtimefec/js/styles.json', function(error, s) {
d3.json('http://assets.realtime.influenceexplorer.com.s3.amazonaws.com/1.0/realtimefec/js/styles.json', function(error, s) {

    
        var circle_radius = 4;
        // Parameters for top-level sizing of plot
        var blog_or_feature = 'blog';
        var desired_height = 350;
        var div_selector = "#line-chart";
        // If there are too many items the legend won't fit
        var drawLegend = true;

        // list of colors
        var available_colors = ['yellows', 'teals', 'reds', 'pinks', 'mints', 'magentas', 'oranges', 'blues', 'cyans', 'greens'];
        var num_colors = 5;
        var colors = [];
        
        for (var i=0; i<num_colors; i++) {
            colors[i] = s.colors.network_graph[available_colors[i]][0].hex;
        }
        
        d3.json(window.datafileURL, function(error, data) {
            
            var svg = d3.select(div_selector+' svg');

            var raw_data = data['results'];
            //Sort this to be sure.
            raw_data = raw_data.sort(compare);
            
            var yFormatter = d3.format(",.0$");
            var parseDate = d3.time.format("%Y-%m-%d").parse;

            // hash data
            var district_ids = {};
            var dates = {};
            var dateindex = 0;
            
            // Group the data by district
            
            raw_data.forEach(function(d) {
            
                var this_date =  parseDate(d['end_date']);
                var this_data_obj = {'date':this_date, 'value':null_or_float(d['outside_spending']), 'id':d['district']['id']};
                
                if (!(this_date in dates)) {
                    dates[this_date] = this_date;
                }
                
                if ((d['district']['id'] in district_ids )) {
                    // The key exists, so just push the latest data element
                    district_ids[d['district']['id']]['values'].push(this_data_obj)
                    }
                else {
                    // it's new, so create the thing
                    district_ids[d['district']['id']] = {'id': d['district']['id'], 'name':d['district']['race_name'], 'values':[this_data_obj]};

                }
            });
            
            // hash the colors
            var color_dict = {}
            var color_index = 0;
            for (var key in district_ids ) {
                color_dict[key] = colors[color_index++];
            }
            
            data_array = [];
            // Transform the grouped district data into an array 
            for (var key in district_ids) {
                data_array.push(district_ids[key]);
            }
            
            var maxValue = d3.max(raw_data, function(c) { return null_or_float(c.outside_spending)});
            
            /*
             * Setting margins according to longest yAxis label, default to styles.json
             */

            //  ... get default margins from specs
            var margin = s.plot_elements.canvas.margin;

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
            var suggestedLeftMargin = yLabelWidth + parseInt(s.text_styles.axis_title['font-size']) + s.plot_elements.axis.title_padding;

            margin.left = Math.max(margin.left, suggestedLeftMargin);

            //  ... follow D3 margin convention as normal
            var width = s.plot_elements.canvas.width[blog_or_feature] - margin.left - margin.right,
                height = desired_height - margin.top - margin.bottom;

            svg.attr("width", width + margin.left + margin.right)
               .attr("height", height + margin.top + margin.bottom);

            /*
             * Creating scales
             */

            var x = d3.time.scale()
                    .range([0, width]);

            var y = d3.scale.linear()
                    .range([height, 0]);
            
            var mindate = d3.min(d3.values(dates));
            var maxdate = d3.max(d3.values(dates));
            
            var xmin = d3.time.day.offset(mindate, -1);
            var xmax = d3.time.day.offset(maxdate, 1);
            

            x.domain([xmin, xmax]);            
            y.domain([0, maxValue + 100000]);


            /*
             * Creating Axes and Gridlines (innerTick)
             */
            var xAxis = d3.svg.axis()
                .ticks(3)
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
            
                var legendx = 70;
                var legendy = 340;
                var legend_width = 360;
                var legend_height = 40;
            
                var legend_inner_padding = 3;
                var sample_line_voffset = 5;
                var sample_line_length = 20;
                var text_x_offset = 3;

                // We draw left to right. Track where we are here
                var xcursor_position = legendx;
                
                // This could be set dynamically, but... 
                var num_items = 3;
            
                for (var i = 0; i < num_items; i++) {
                
                    var this_color = color_dict[data_array[i]['id']];
                    var this_name = data_array[i]['name'];
                
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
                            .style("fill", s.text_styles.point_label.color)
                            .style("font-family", s.text_styles.point_label['font-family'])
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
                .attr("y", function() { return -(margin.left - s.plot_elements.axis.label_padding);})
                .attr("dy", function() { return s.text_styles.axis_label['font-size']; })
                .style("text-anchor", "middle")
                .text("Total independent expenditures reported");

            // line drawing function
            var line = d3.svg.line()
                //.interpolate("basis")
                .x(function(d) { return x(d.date); })
                .y(function(d) { return y(d.value); });

            var chart_data = lineChart.selectAll(".party")
                .data(data_array)
              .enter().append("g")
                .attr("class", "party");

            chart_data.append("path")
                .attr("class", "line")
                .attr("d", function(d) { return line(d.values); })
                .style("stroke-width", 3)
                .style("fill", "none")
                .style("stroke", function(d) {  return color_dict[d['id']] });

            var point = chart_data.append("g")
                .attr("class", "line-point");

            point.selectAll("circle")
                .data(function(d,i){ return d.values; })
              .enter().append("circle")
                .attr("cx", function(d) { return x(d.date); })
                .attr("cy", function(d) { return y(d.value); })
                .attr("r", circle_radius)
                .style("fill", function(d) { return color_dict[d['id']]; })
              
            
            /*  DON'T DRAW NUMERIC LABELS ON POINTS -- THESE GET TOO CROWDED. 
            var point_labels = party.append("g")
                .attr("class", "point-label");

            point_labels.selectAll("text")
                .data(function(d,i){ return d.values; })
              .enter().append("text")
                .style("fill", s.text_styles.point_label.color)
                .style("font-size", s.text_styles.point_label['font-size'])
                .style("font-family", s.text_styles.point_label['font-family'])
                .attr("x", function(d) { return x(d.date); })
                .attr("y", function(d) { return y(d.amount); })
                //.attr("dx", function(d) { return -(longestLabel); })
                .style("text-anchor","end")
                .attr("dy", function(d) { return -(parseInt(s.text_styles.point_label['font-size']) / 3);})
                .attr("dx", -5)
                .text(function(d) { return "$" + yFormatter(d.amount); })
            */

        });

});

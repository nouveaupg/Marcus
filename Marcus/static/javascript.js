function refreshDataAjax() {
  var data_dump = JSON.stringify({"action":"getCameraData"});
  $.post("json-api/",data_dump,function(data,textStatus,jqXHR){
    response_data = JSON.parse(data);
    if (response_data['success'] == true) {
      var camera_data = response_data["cameras"];
      for( each in camera_data ) {
        var timeslider_id = "#timeslider_" + each;
        var widget = $(timeslider_id);
        widget.slider("option","min",0);
        widget.slider("option","max",camera_data[each]["frames"]-1);
        widget.slider("value",camera_data[each]["frames"]-1);
        $(timeslider_id + " span").css("left","100%");
        d = new Date(camera_data[each]['latest_frame_timestamp']);
        console.log(d);
        $("#timestamp_" + each).text(d.toLocaleString());
      }
    }
    else {
      alert("Error updating camera(s)!");
    }
  });
}

function getFrameInfo(camera_uuid,frame_offset) {
  var data_dump = JSON.stringify({"action":"get_frame_info",
                                  "camera_uuid":camera_uuid,
                                "offset":frame_offset});
  $.post("json-api/",data_dump,function(data,textStatus,jqXHR){
    response_data = JSON.parse(data);
    if (response_data['success'] == true) {
      $("#camera_frame_" + camera_uuid).attr('src',"uploaded_images/" + response_data['frame_url']);
      d = new Date(response_data['frame_timestamp']);
      $("#timestamp_" + camera_uuid).text(d.toLocaleString());
    }
    else {
      alert("Error retrieving frame.");
    }
  });
}

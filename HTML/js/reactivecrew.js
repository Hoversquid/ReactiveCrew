window.addEventListener("DOMContentLoaded", () => {
  const websocket = new WebSocket("ws://localhost:8001/");
  // init(websocket);
  startWebsocket(websocket);
});

function startWebsocket(websocket) {

  websocket.addEventListener("message", ({ data }) => {
    
    const event = JSON.parse(data);
    console.log('event type: ' + event.type);
    if (event.type == 'switch') {

      switchMainIcon(
        JSON.parse(event.indexes),
        event.oldMainIndex,
        event.newMainIndex,
        event.mainIconWidth,
        event.img_width,
        event.img_height,
        event.max_column,
        event.mainIconTop,
        event.mainNameSize,
        event.nameSize,
        event.name_offset
      );
      let again = { type: 'response' };
      websocket.send(JSON.stringify(again));

  } else if (event.type = 'refresh') {
    console.log('event type: ' + event.type);
    location.reload(true);
    switchMainIcon(
      JSON.parse(event.indexes),
      event.oldMainIndex,
      event.newMainIndex,
      event.mainIconWidth,
      event.img_width,
      event.img_height,
      event.max_column,
      event.mainIconTop,
      event.mainNameSize,
      event.nameSize,
      event.name_offset
    );
    let again = { type: 'response' };
    websocket.send(JSON.stringify(again));
  }

  });
}

function switchMainIcon(
  indexes, oldMainIndex, newMainIndex,
  mainIconWidth, img_width, img_height, 
  max_column, mainIconTop, mainNameSize, nameSize, nameOffset) {

  var bigDiv = document.getElementById('big-div');
  bigDiv.classList.remove("fade-div");
  bigDiv.offsetWidth;
  bigDiv.classList.add("fade-div");

  curr_index = newMainIndex;
  var offset = 0;

  if (indexes.indexOf(parseInt(newMainIndex)) != -1) {

    var num_rows = Math.floor((indexes.length - 2) / max_column);
    var imagePosAmt;

    if (num_rows > 0) {

      imagePosAmt = Number(img_height) + Number(nameSize);

    } else {
      imagePosAmt =  Number(mainIconTop) + (Number(mainNameSize) / 2) + Number(nameSize);
      num_rows = 1
    }

    console.log('num_rows: ' + num_rows);

    for (var i = 0; i < indexes.length; i++) {

      var index = indexes[i];
      var selectedDiv = document.getElementById("crew-" + index);
      var column = offset % max_column;
      var row = Math.floor(offset / max_column);
      
      if (index != newMainIndex) {

        if (index == oldMainIndex) {
          // change current main icon to a standard icon
          selectedDiv.classList.add('crew-plate');
          selectedDiv.classList.remove('main-plate');
          selectedDiv.lastChild.style.position = 'static';
          selectedDiv.lastChild.style.top = 0;
        }

        console.log('row: ' + row);
        selectedDiv.style.left = (Number(mainIconWidth) + (column * Number(img_width)));
        selectedDiv.style.top = ((Number(num_rows) - row) * imagePosAmt);
        offset++;
        
      } else {
        // change selected icon to a main icon
        selectedDiv.classList.add('main-plate');
        selectedDiv.classList.remove('crew-plate');
        selectedDiv.style.top = Number(mainIconTop);
        selectedDiv.style.left = 0;
        selectedDiv.lastChild.style.position = 'relative';
        selectedDiv.lastChild.style.top = Number(nameOffset);
      }
    }
  }
}
window.addEventListener("DOMContentLoaded", () => {
  const websocket = new WebSocket("ws://localhost:8001/");
  // init(websocket);
  startWebsocket(websocket);
});

function init(websocket) {
  let event = { type: 'init' };
  websocket.send(JSON.stringify(event));
}

function startWebsocket(websocket) {

  console.log('started websocket')
  websocket.addEventListener("message", ({ data }) => {
    
    const event = JSON.parse(data);
    console.log('event: ' + event);
    if (event.type == 'refresh') {
      location.reload(); 
      console.log('reloading')
    } 
    if (event.indexes) {
      switchMainIcon(
        JSON.parse(event.indexes),
        event.oldMainIndex,
        event.newMainIndex,
        event.mainIconWidth,
        event.img_width,
        event.img_height,
        event.max_column,
        event.mainIconTop,
        event.nameSize,
        event.name_offset
      );
    }
    let again = { type: 'init' };
    websocket.send(JSON.stringify(again));
  });

}

function switchMainIcon(
  indexes, oldMainIndex, newMainIndex,
  mainIconWidth, img_width, img_height, 
  max_column, mainIconTop, nameSize, nameOffset) {

  var bigDiv = document.getElementById('big-div');
  bigDiv.classList.remove("fade-div");
  bigDiv.offsetWidth;
  bigDiv.classList.add("fade-div");
  
  var offset = 0;
  console.log('mainIconTop: ' + mainIconTop);
  console.log('newMainIndex: ' + newMainIndex);
  console.log('oldMainIndex: ' + oldMainIndex);
  console.log('indexes: ' + indexes);
  console.log('test: ' + indexes.indexOf(parseInt(newMainIndex)));
  console.log('Number(nameOffset): ' + Number(nameOffset));
  console.log('-----------------');

  // const array =  indexes;
  if (indexes.indexOf(parseInt(newMainIndex)) != -1) {
    var num_rows = Math.floor((indexes.length - 2) / max_column);
    console.log('row offset: ' + Number(num_rows));

    for (var i = 0; i < indexes.length; i++) {
      // console.log('i: ' + i);
      // console.log('index: ' + indexes[i]);

      var index = indexes[i];
      var selectedDiv = document.getElementById("crew-" + index);
      var column = offset % max_column;
      var row = Math.floor(offset / max_column);
      
      if (index != newMainIndex) {

        if (index == oldMainIndex) {
          // change current main icon to a standard icon
          console.log('changing index: ' + i + ' to regular plate');

          selectedDiv.classList.add('crew-plate');
          selectedDiv.classList.remove('main-plate');
          selectedDiv.lastChild.style.position = 'static';
          selectedDiv.lastChild.style.top = 0;
        }

        selectedDiv.style.left = (Number(mainIconWidth) + (column * Number(img_width)));
        selectedDiv.style.top = ((Number(num_rows) - row) * (Number(img_height) + Number(nameSize)));
        // selectedDiv.style.top = ((Number(num_rows) - row) * (Number(img_height) + Number(nameSize)));
        // selectedDiv.style.top = ((Number(max_row) - row) * (Number(img_height) + Number(nameSize)));

        // console.log('selectedDiv ' + index  + '- left: ' + selectedDiv.style.left);
        // console.log('selectedDiv ' + index  + '- top: ' + selectedDiv.style.top);
        offset++;
        
      } else {
        console.log('changing index: ' + i + ' to main plate');
        // change selected icon to a main icon
        selectedDiv.classList.add('main-plate');
        selectedDiv.classList.remove('crew-plate');
        // selectedDiv.style.top = 0;
        selectedDiv.style.top = Number(mainIconTop);
        // selectedDiv.style.top = Number(mainIconTop);
        selectedDiv.style.left = 0;
        selectedDiv.lastChild.style.position = 'relative';
        selectedDiv.lastChild.style.top = Number(nameOffset);
        // selectedDiv.lastChild.style.top = Number(mainIconTop);
        // selectedDiv.lastChild.style.top = Number(mainIconTop) * 0.75;
      }
    }
  }
}
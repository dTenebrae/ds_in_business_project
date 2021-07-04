$(function () {
    var canvas = $('.whiteboard')[0];
    var context = canvas.getContext('2d');
    var sendBtn = $('#send-btn');
    var clearBtn = $('#clear-btn');
    var current = {
        color: 'black'
    };
    var drawing = false;

    function drawLine(x0, y0, x1, y1, color) {
        context.beginPath();
        context.moveTo(x0, y0);
        context.lineTo(x1, y1);
        context.strokeStyle = color;
        context.lineWidth = 4;
        context.stroke();
        context.closePath();
    }

    function onMouseDown(e) {
        drawing = true;
        current.x = e.clientX;
        current.y = e.clientY;
    }

    function onMouseUp(e) {
        if (!drawing) { return; }
        drawing = false;
        drawLine(current.x, current.y, e.clientX, e.clientY, current.color);
    }

    function onMouseMove(e) {
        if (!drawing) { return; }
        drawLine(current.x, current.y, e.clientX, e.clientY, current.color);
        current.x = e.clientX;
        current.y = e.clientY;
    }

    function sendEvent() {
        var dataURL = canvas.toDataURL();
        console.log(dataURL);
        $.ajax({
          type: "POST",
          url: "hook",
          data:{
            imageBase64: dataURL
          }
        }).done(function() {
          console.log('sent');
        });
        context.clearRect(0, 0, canvas.width, canvas.height);
    }

    function clearBoard() {
        context.clearRect(0, 0, canvas.width, canvas.height);
    }
    
    function onResize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('mouseout', onMouseUp);
    canvas.addEventListener('mousemove', onMouseMove);
    
    sendBtn.on('click', sendEvent);
    clearBtn.on('click', clearBoard);


    window.addEventListener('resize', onResize);
    onResize();
});

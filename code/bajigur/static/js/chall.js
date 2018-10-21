function updatefiles(){
    var form = $('#modalfiles form')[0];
    var formData = new FormData(form);
    var chal = document.getElementById("challid").value
    $.ajax({
        url: script_root + '/admin/files/'+chal,
        data: formData,
        type: 'POST',
        cache: false,
        contentType: false,
        processData: false,
        success: function(data){
            form.reset();
            loadfiles(chal);
        }
    });
}

function loadfiles(chal){
    $.get(script_root + '/admin/files/' + chal, function(data){
        $('#files-chal').val(chal);
        var files = $.parseJSON(JSON.stringify(data));
        var files = files['files'];
        $('#current-files').empty();
        for(var x = 0; x < files.length; x++){
            var filename = files[x].file.split('/');
            var filename = filename[filename.length - 1];
            var curr_file = "<tr>\
                <td><a href='"+ script_root + "/files/" + files[x].file + "'>" + filename + "</a></td> \
                <td><button id='delete' type='button' class='btn btn-danger' onclick=\"" + "deletefile('" + files[x].id + "',$(this),'" + files[x].challid + "','" + files[x].file +"')\" >Delete</button></td>\
                    </tr>";
            $('#current-files').append(curr_file);
        }

        $("#modalfiles").modal("show");
    });
}

function deletefile(id,elem,challid,location){
    $.ajax({
        url: script_root + '/admin/files/'+ challid,
        data: {'method' : 'delete','id' : id,'location' : location},
        type: 'POST',
        cache: false,
        success: function(data){
            if(data == "1"){
                elem.parent().parent().remove()
            }
        }
    });
}

function editchall(id,elem){
    $.ajax({
        url: script_root + '/admin/challenge/edit/' + id,
        data: {'id' : id},
        type: 'GET',
        cache: false,
        success: function(data){
            document.getElementById("namasoal").value = data.name;
            document.getElementById("tipesoal").value = data.tipe;
            document.getElementById("deskripsisoal").value = data.deskripsi;
            document.getElementById("poinsoal").value = data.poin;
            document.getElementById("flagsoal").value = data.flag;
            document.getElementById("formchall").action = script_root + "/admin/challenge/edit/" + id;
            $("#modalchalls").modal("show");           
        }
    });
}

function setHidden(id,element){
    var status = element.parent().attr("id");
    var context = element.attr("id");
    $.ajax({
        url: script_root + '/admin/sethidden',
        data: {'status': status,"id": id,"context": context},
        type: 'POST',
        cache: false,
        success: function(data){
            element.parent().attr("id",data);
            element.removeClass();
            if(data == 'Hidden'){
                element.text("Hidden");
                element.addClass("btn btn-danger pullright");
            }
            else{
                element.text("Active"); 
                element.addClass("btn btn-success pullright");
            }
        }
    });
}

$(document).ready(function () {
    $('button').click(function(){
        var tes = $(this).attr('id') ;
        var challid = $(this).parent().parent().attr('id');
        if(tes =="modalfile"){
            document.getElementById("challid").value = challid;
            loadfiles(challid);
        }
        else if(tes == "modalchall"){
            if(challid){
                editchall(challid,$(this));
            }
            $("#"+tes+"s").modal("show");
        }
        else if(tes == "team" || tes == "soal"){
            setHidden(challid,$(this));
        }
    });

    $('#submit-files').click(function (e) {
        e.preventDefault();
        updatefiles()
    });

    notif_msg = $("#notif_msg");
    if(notif_msg){
        notif_msg.slideUp(2500);
    }

});

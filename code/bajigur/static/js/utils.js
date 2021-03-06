function showchall(id){
    $.ajax({
        url: script_root + '/challenge/'+ id,
        data: {'id' : id},
        type: 'GET',
        cache: false,
        success: function(data){
            $("#tempat_file").empty();
            for(var x=0 ; x < data['files'].length ; x++){
                var nama_file = data['files'][x].split('/')[1];
                var list_file = "<li><a href='" + "/files/" + data['files'][x] + "'>" + nama_file +"</a></li>";
                $("#tempat_file").append(list_file);
            }
            document.getElementById("chall_title").innerHTML = data.name;
            document.getElementById("chall_poin").innerHTML = data.poin;
            document.getElementById("chall_deskripsi").innerHTML = data.deskripsi;
            document.getElementById("soal_id").value = data.id;
//	    $("#challmodal").modal("show");
        }
    });
}


function show_solves(id){
    $.ajax({
        url : script_root + '/challenge/' + id,
        data : {'methodd' : "show_solves"},
        type : 'POST',
        cache : false,
        success: function(data){
            $("#tempat_solves").empty();
            for(var i=0 ; i < data.length ; i++){
                if(data[i].hidden == 'false'){
                    var team_id = data[i].id;
                    var team_name = data[i].name;
                    var solve_time = data[i].solve_time.replace("GMT","WIB");
                    var payload = "<tr>\
                                        <td><a href='" + "/team/" + team_id +"'>" + team_name + "</a></td>\
                                        <td>" + solve_time + "</td>\
                                    <tr>"
                    $("#tempat_solves").append(payload);
                }
            }
        }
    });
}

function sendflag(){
    var form = $("#details form")[0];
    var formData = new FormData(form);
    var id = $("#soal_id").attr('value');
    $.ajax({
        url : script_root + '/challenge/' + id,
        data : formData,
        type : 'POST',
        cache : false,
        contentType: false,
        processData: false,
        success: function(data){
            form.reset();
            if(data.notifsuccess){
                document.getElementById("notifmodal").className = "alert alert-success text-center";
                document.getElementById("notifmodal").innerHTML = data.notifsuccess;
                document.getElementById(id).style.backgroundColor = "#16CB34";
            }
            else{
                document.getElementById("notifmodal").className = "alert alert-danger text-center";
                document.getElementById("notifmodal").innerHTML = data.notiffail;
            }

            $("#challmodal").modal("show");
            tes = $("#notifmodal");
            tes.slideDown(250);
            tes.slideUp(1800);

        }
    });
}


function CloseChall(){
    $("#tempat_file").empty();
    document.getElementById("chall_title").innerHTML = "";
    document.getElementById("chall_poin").innerHTML = "";
    document.getElementById("chall_deskripsi").innerHTML = "";
    document.getElementById("soal_id").value = "";
}

$(document).ready(function () {
    $("button").click(function(){
        var tes = $(this).attr('id')
        var id_parent = $(this).parent().parent().attr('id');
        if(id_parent == 'challss'){
            show_solves(tes);
            showchall(tes);
            $("#challmodal").modal("show");
        }
    });

    $("#submitflag").click(function(){
        $("#details form").submit();
    })
    $("#details form").on('submit', function (e) {
        e.preventDefault();
        sendflag();
    });

    // $("#solves").click(function(){
    //     show_solves($(this));
    // })

    notif_msg = $("#notif_msg");
    if(notif_msg){
        notif_msg.slideUp(2700);
    }

    $('#challmodal').on('hidden.bs.modal', function (e) {
        CloseChall();
    });

});



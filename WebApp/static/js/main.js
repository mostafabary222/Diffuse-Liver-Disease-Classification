$(document).ready(function() {

    $('#loginButton').click(function() {
        $('#loginModal').modal('toggle');
    })
})

// function toggleEditReport() {
//     value = $(#card).find('dd.name').html()
//     $('#name').replaceWith('<input name="name" id="#name" type="text" value="' + value + '"> ')
// }

function generatePassword() {
    var string =(Math.random() + 1).toString(36).substring(2);
    document.getElementById("pass").value = string;
    document.getElementById("save").removeAttribute("hidden"); 
    document.getElementById("copy").removeAttribute("hidden"); 
}

function copyPassword() {
    var copyText = document.getElementById("pass");
    copyText.select();
    navigator.clipboard.writeText(copyText.value); 
}

// function savePassword() {
//     // alert("success");
//     s = document.getElementById("password").value
//     alert(s);
//     $.ajax({
//         method: 'POST',
//         type: "POST",
//         dataType: 'json',
//         url: '{% url "patients" %}',
//         data: {s, csrfmiddlewaretoken: '{{ csrf_token }}'},
//         success: alert("it worked"),
//         error: alert("didnt work")
//     });
// }
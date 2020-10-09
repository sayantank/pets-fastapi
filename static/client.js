const petsForm = document.getElementById("pets-form")

// This eventListener is called on submitting the form
petsForm.addEventListener('submit', (e) => {
    // Prevents the page to refresh on submitting
    e.preventDefault()
    
    var loc = window.location;
    
    // Gets the latest uploaded file
    var img_upload = document.getElementById("file-input").files[0]
    
    // Used to read our file
    const reader = new FileReader();
    
    
    if(img_upload && (img_upload.type == "image/jpeg" || img_upload.type == "image/png")){
        // Encodes the file to base64
        reader.readAsDataURL(img_upload);
    } else {
        alert("Invalid file")
    }
    
    // This eventListener is called when the read operation completes
    reader.addEventListener("load", function() {
        fetch(`${loc.protocol}//${loc.hostname}:${loc.port}/upload`, {
            method: "post",
            body: JSON.stringify({
                "img_base64": reader.result
            })
        }).then((res) => {
            return res.json()
        }).then((json) => {
            document.getElementById("pred").innerHTML = `This pet is a ${json['pred']}`
        })
    }, false)
})
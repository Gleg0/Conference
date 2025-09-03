const backBtn = document.getElementById("back-btn");
if (backBtn) {
    backBtn.addEventListener("click", function(event) {
        event.preventDefault();
        history.back();
    });
}

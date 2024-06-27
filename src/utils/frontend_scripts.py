
custom_html="""
<script>
var doc = window.parent.document;

function clickButton(label) {
    var buttons = doc.querySelectorAll('label div > p');
    buttons.forEach((pElement) => {
        if (pElement.innerText.startsWith(label)) {
            pElement.closest("label").click();
        }
    });
}

doc.addEventListener('keydown', function(e) {

    // Check if the key code is between 49 (key '1') and 59 (key ':')
    if (e.keyCode >= 49 && e.keyCode <= 59) {
        // Calculate the corresponding button string
        const keyChar = String.fromCharCode(e.keyCode);
        clickButton(`${keyChar}:`);
    }

    switch (e.keyCode) {
        case 37: // (37 = left arrow)
            doc.querySelector('.step-down').click();
            break;
        case 39: // (39 = right arrow)
            doc.querySelector('.step-up').click();
            break;
    }
});
</script>
"""

# Define your custom CSS
custom_css = """
<style>
header, footer, [data-testid="stSidebarHeader"] {
  visibility: hidden;
  display: none;
}
.main .block-container {
  padding: 0rem 2rem 0rem 2rem;
}
#root > div:nth-child(1) > div.withScreencast > div > div > div > section > div > div {
  padding-top: 0em !important;
}
.stAlert a {
word-break: break-all;
}
</style>
"""

custom_html="""
<script>
var doc = window.parent.document;

function toggleButton(label) {
    var buttons = doc.querySelectorAll('label div > p');
    buttons.forEach((pElement) => {
        if (pElement.innerText.startsWith(label)) {
            pElement.closest("label").click();
        }
    });
}

function clickButton(label) {
    var buttons = doc.querySelectorAll('.stButton button');
    buttons.forEach((pElement) => {
        if (pElement.innerText.startsWith(label)) {
            pElement.click();
        }
    });
}

doc.addEventListener('keydown', function(e) {

    // if the cursors is in a textare or input, don't trigger the shortcuts
    if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON') {
        // Select all <p> elements
        const paragraphs = doc.querySelectorAll('div[data-testid="stExpander"] > details > summary > span > div > p');
        console.log(paragraphs);
        console.log("reach");

        // Iterate through each <p> element
        paragraphs.forEach(paragraph => {
            // Check if the text content of the <p> element is "Keyboard shortcuts"
            if (paragraph.textContent.trim() === 'Keyboard shortcuts') {
                // gray out the text
                paragraph.style.color = 'gray';
            }
        });

        return;
    }

    // Check if the key code is between 48 (key '0') and 58 (key '9')
    console.log(e.keyCode)
    if (e.keyCode >= 48 && e.keyCode <= 58) {
        // Calculate the corresponding button string
        const keyChar = String.fromCharCode(e.keyCode);
        toggleButton(`${keyChar}:`);
    }

    // if F or f is pressed, click the Find button
    if (e.keyCode === 70 || e.keyCode === 102) {
        if (!event.ctrlKey) {
            clickButton('Find next incomplete task');
        }
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
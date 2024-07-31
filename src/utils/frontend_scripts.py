
custom_html="""
<script>
var doc = window.parent.document;

// Select all <p> elements
const expanders = doc.querySelectorAll('div[data-testid="stExpander"] > details > summary > span > div > p');
var shortcut_expander = null;

// Iterate through each <p> element
expanders.forEach(expander => {
    // Check if the text content of the <p> element is "Keyboard shortcuts"
    if (expander.textContent.trim().startsWith('Keyboard shortcuts')) {
        // Save the expander element
        shortcut_expander = expander;
    }
});

function attachEventListeners() {
    var elements = doc.querySelectorAll('textarea, input, button[role="tab"]');
    elements.forEach(element => {
        // if element is not of type checkbox, attach the event listeners
        if (element.type !== 'checkbox') {
            element.addEventListener('focus', handleFocus);
            element.addEventListener('blur', handleBlur);
        }
    });
}

function handleFocus(e) {
    window.shortcutDisabled = true;
    //gray out the keyboard shortcuts
    shortcut_expander.style.color = "gray";
    shortcut_expander.textContent = "Keyboard shortcuts (disabled)";
}

function handleBlur(e) {
    window.shortcutDisabled = false;
    //restore the color of the keyboard shortcuts
    shortcut_expander.style.color = "black";
    shortcut_expander.textContent = "Keyboard shortcuts";
}

// Initial check in case elements already exist
attachEventListeners();


// MutationObserver callback function
function onMutation(mutationsList, observer) {
    for (let mutation of mutationsList) {
        if (mutation.type === 'childList') {
            // Re-attach event listeners in case new elements are added to the DOM
            attachEventListeners();
        }
    }

    // necessary to refresh when, e.g., the text input is used to jump to a specific task
    // because the element is changed 
    var elements = doc.querySelectorAll('textarea, input, button[role="tab"]');
    shortcut_expander.style.color = "black";
    window.shortcutDisabled = false;
    elements.forEach(element => {
            
        if (element.type !== 'checkbox') {
            // print the text of the element
            // if element has the focus, disable the shortcuts
            if (element === doc.activeElement) {
                window.shortcutDisabled = true;
                //gray out the keyboard shortcuts
                shortcut_expander.style.color = "gray";
            }
        }
    });

}

// Create an instance of MutationObserver and specify the callback function
const observer = new MutationObserver(onMutation);

// Options for the observer (which mutations to observe)
const config = { childList: true, subtree: true };

// Start observing the document body for DOM mutations
// observer.observe(doc.body, config);

// Start observing the document body for DOM mutations only on data-testid="stSidebar"
const sidebar = doc.querySelector('[data-testid="stSidebar"]');
if (sidebar) {
    observer.observe(sidebar, config);
}


function toggleButton(label) {
    var buttons = doc.querySelectorAll('label div > p');
    buttons.forEach((pElement) => {
        if (pElement.innerText.startsWith(label)) {
            pElement.closest("label").click();
            // remove the focus from the button
            pElement.blur();
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
    if (window.shortcutDisabled) {
        return;
    }

    // Check if the key code is between 48 (key '0') and 58 (key '9')
    if (e.keyCode >= 48 && e.keyCode <= 58) {
        // Calculate the corresponding button string
        const keyChar = String.fromCharCode(e.keyCode);
        toggleButton(`${keyChar}:`);
    }

    // if F | f | = is pressed, click the Find button
    if (e.keyCode === 70 || e.keyCode === 102 || e.keyCode === 61) {
        clickButton('Find');
    }

    // if w | . | + | ] | Enter is pressed, click the .step-down button
    if (e.keyCode === 87 || e.keyCode === 190 || e.keyCode === 187 || e.keyCode === 221 || e.keyCode === 13) {
        doc.querySelector('.step-up').click();
    }

    // if q | , | - | [ | Backspace" is pressed, click the .step-up button
    if (e.keyCode === 81 || e.keyCode === 188 || e.keyCode === 173 || e.keyCode === 219 || e.keyCode === 8) {
        doc.querySelector('.step-down').click();
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
iframe {
  background-color: #fff;
}

</style>
"""

class WelcomePage():

    def __init__(self, st):
        self.st = st

    def set_user_id(self):
        """
        Set the user ID and update the annotator ID in the STATE object.

        This function retrieves the user ID from the STATE object and sets it as the annotator ID.
        It also updates the query parameters with the annotator ID using st.experimental_set_query_params().

        """
        user_id = self.st.session_state.input_user_id
        self.st.session_state.annotator_id = user_id
        self.st.experimental_set_query_params(annotator_id=user_id)

    # =================== LAYOUT ===================

    def show(self):
        with self.st.form("form_user_id"):

            # Display warning message if no user ID is provided
            self.st.error(
                'No user ID detected. Please enter a user ID below.', icon="🚨")
            user_id = self.st.text_input(
                "Annotator Name:", help="Your Name", key='input_user_id')

            submit_button = self.st.form_submit_button(
                "Load Tasks", on_click=self.set_user_id)

            # Handle form submission
            if submit_button:
                if user_id:
                    self.st.success(
                        f"User ID '{user_id}' submitted successfully!")
                else:
                    self.st.warning("Please enter a User ID.")

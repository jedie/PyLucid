# -*- coding: utf-8 -*-

"""
    PyLucid Plugin API example
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Pseudocode!

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from PyLucid.system.BasePlugin import PyLucidBasePlugin

class ExamplePlugin(PyLucidBasePlugin):
    """
    We inherit from the base plugin.
    """
    def global_objects(self):
        """
        A list of all global plugin objects how inherit from the base plugin.
        """
        # The plugin name as a String:
        self.plugin_name

        # Interface to the internal pages (only for special needs)
        # PyLucid.system.internal_page.InternalPage()
        self.internal_page

        # The global context
        self.context

        # A response object (only for special needs)
        self.response

        # The django request object
        # see http://www.djangoproject.com/documentation/request_response/
        self.request

        # Interface to the PyLucid page message system
        self.page_msg

        # object to build URLs:
        # comes from PyLucid.system.URLs
        self.URLs

        # database instance of the cms page object:
        self.current_page

    #__________________________________________________________________________
    # URLs
    #
    # How to build urls
    #
    def building_urls(self):
        """
        You should never building urls "by hand". You should use URLs!
        In the most case you need only methodLink() and commandLink().

        In special cases you can some other methods. Please look into the
        source code PyLucid.system.URLs
        """
        # mostly you will create a link to a other method of the current plugin
        # Use methodLink() for this:
        link = self.URLs.methodLink("method_name")

        # In special cases you would like to insert a link to a other plugin.
        # Use commandLink() for this:
        link = self.URLs.commandLink("page_admin", "edit_page")

        # The URLs object is a dictionary like object. You can display the
        # content of it into the page_msg with:
        self.URLs.debug()


    #__________________________________________________________________________
    # OUTPUT
    #
    # How a Plugin can create a response
    #
    def render_a_internal_page(self):
        """
        Normal way to create output into the content area with a existing
        internal page.

        See also: http://pylucid.org/_goto/142/internal-pages/
        """
        # Example:
        context = {
            # Building a template context for the internal page
            "key": value,
            "Foo": Bar,
        }
        # Render the template with the context and write the result into the
        # response object:
        self._render_template("InternalPageName", context)

    def page_msg(self):
        """
        With the global self.page_msg object a plugin can easy send short
        messages to the user.
        You can call page_msg several times and everywhere.
        All messages would be inserted in the generated page.

        Note:
            The page message object is good for debugging. List and Dictioaries
            would be formatted with pprint.

        More info in PyLucid.system.page_msg
        """
        # Examples:

        # Normal ouput in blue color
        self.page_msg("The shorted way...")

        # A error in red color
        self.page_msg.red("Error!")

        # A black colored messages:
        self.page_msg.black("I am black")

        # Successfull messages should be geen:
        self.page_msg.green("Update XY successfull")

    def return_a_response(self):
        """
        A Plugin method can return a django HttpResponse object directy back.
        e.g. send files to the client or a Redirect
        """
        # send the XML file to the client
        from django.http import HttpResponse
        response = HttpResponse()
        response['Content-Type'] = 'application/xml; charset=utf-8'
        response.write(FooBar)
        return response

    def change_page_title(self):
        """
        If a plugin creates his own response page, it should be change the
        current displayed page title, so it makes more sense for the user.
        """
        self.context["PAGE"].title = "The Plugin Title"

    #__________________________________________________________________________
    # PREFERENCES
    #
    def get_my_preferences(self):
        """
        more info about plugin preferences:
            http://www.pylucid.org/_goto/153/preferences/
        """
        # Get the preferences from the database:
        preferences = self.get_preferences()

        # Get a entry (It's a dict api)
        my_entry_value = preferences["entry_key"]

    def change_preference_entry(self):
        """
        A plugin can change a preference entry with self.set_preferences()
        """
        new_preference_dict = self.set_preferences("key", "new_value")

        self.page_msg("Changed value:", new_preference_dict["key"])

    #__________________________________________________________________________
    # ENVIRONMENT
    #
    # Some needfull information
    #
    def on_request_object(self):
        """
        Some needfull objects from the request object.
        """
        # Is debug on? If you will display information only if debug is on, you
        # should not use settings.DEBUG directly!
        # Use request.debug, because it is true if settings.DEBUG if true *or*
        # if the client IP is in settings.INTERNAL_IPS
        # This is append to the request object in
        # PyLucid.system.utils.setup_debug
        if self.request.debug:
            self.page_msg("Debug is on.")

    #__________________________________________________________________________
    # UTILS
    #
    # Some needfull methods
    #
    def simple_error_feedback(self):
        """
        with self.error() you can easy create a "abort" error messages.
        The goal is: The method gets two messages types:
            public_msg, debug_msg
        The public messages would be always displayed. The debug messages would
        be append if self.request.debug is on.
        So you can easy gives feedback for anonymous users and developers, too.
        """
        try:
            print "...do something..."
        except Exception, err:
            return self.error(_("Wrong URL."), err)
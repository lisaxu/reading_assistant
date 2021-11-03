
class HTML_Generator:

    def write_it(self, it, how):
        """
        Opens the file (name set during object creation), writes, and closes
        """
        f = open(self.outfile, how)
        f.write(it)
        f.close()

    def __init__(self, outfile, name):
        """
        As part of the creation process, the output file is started
        """
        self.outfile = outfile
        self.name = name
        outstr = '''
            <!-- source: W3 Schools https://www.w3schools.com/howto/howto_js_collapsible.asp -->
            <!DOCTYPE html>
            <html>
            <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
            .collapsible {
              background-color: #777;
              color: white;
              cursor: pointer;
              padding: 18px;
              width: 100%;
              border: none;
              text-align: left;
              outline: none;
              font-size: 15px;
            }

            .active, .collapsible:hover {
              background-color: #555;
            }

            .collapsible:after {
              content: '\\002B';
              color: white;
              font-weight: bold;
              float: right;
              margin-left: 5px;
            }

            .active:after {
              content: "\\2212";
            }

            .content {
              padding: 0 18px;
              max-height: 0;
              overflow: hidden;
              transition: max-height 0.2s ease-out;
              background-color: #f1f1f1;
            }
            </style>
            </head>
            <body>
            '''
        outstr += "<h2>Rank for: " + self.name + "</h2>"
        self.write_it(outstr, "w")

    def add_divide(self, text):
        """
        A major header
        """
        outstr = "<hr/><hr/><hr/><h1>" + str(text) + "</h1>"
        self.write_it(outstr, "a")

    def add_title(self, text):
        """
        A minor header
        """
        outstr = "<h3>" + str(text) + "</h3>"
        self.write_it(outstr, "a")

    def add_text(self, text):
        """
        <paragraph> text
        """
        outstr = "<p>" + str(text) + "</p>"
        self.write_it(outstr, "a")

    def add_match(self, match_name, match_score, match_text):
        """
        Adds text inside a drop-down
        """
        outstr = "<button class=\"collapsible\"> similarity found: " + str(match_name) + "(score=" + str(match_score) + ") " + "</button>"
        outstr += "<div class=\"content\"><p>" + str(match_text) + "</p></div>"
        self.write_it(outstr, "a")

    def close_file(self):
        """
        Adds footer HTML
        """
        outstr = '''
            <script>
            var coll = document.getElementsByClassName("collapsible");
            var i;

            for (i = 0; i < coll.length; i++) {
              coll[i].addEventListener("click", function() {
                this.classList.toggle("active");
                var content = this.nextElementSibling;
                if (content.style.maxHeight){
                  content.style.maxHeight = null;
                } else {
                  content.style.maxHeight = content.scrollHeight + "px";
                } 
              });
            }
            </script>

            </body>
            </html>
            '''

        self.write_it(outstr, "a")
        
        #print("\nDropping your pen and rubbing your temples, you look over", self.outfile, "and smile knowing the analysis is done.  ")







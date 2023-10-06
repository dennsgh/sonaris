from pages.home import HomePage

def loadPage(self, item):
    page_name = item.text()
    if page_name == "Home":
        self.content = HomePage(self)
    elif page_name == "DG4202":
        
        #self.content = DG4202Page(self)  # You'll need to create this class similar to HomePage
    # ... handle other pages
    self.content_area = self.content

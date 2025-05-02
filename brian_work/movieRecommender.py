import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QTabWidget, 
    QGridLayout, QMessageBox
)
import mysql.connector

from brian_work.tfidf_recommender import build_tfidf_matrix, get_similar_movies

class RecommenderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movie Recommender")
        self.resize(800, 600)
        self.initUI()
        # Build the TF-IDF matrix once on startup for recommendations by overview
        self.df, self.tfidf_matrix, self.tfidf = build_tfidf_matrix()

    def initUI(self):
        # Create a tab widget for two modes: Title Search and Filter Search.
        self.tabs = QTabWidget(self)
        self.tabTitleSearch = QWidget()
        self.tabFilterSearch = QWidget()
        self.tabs.addTab(self.tabTitleSearch, "Search by Title")
        self.tabs.addTab(self.tabFilterSearch, "Filter by Preferences")

        # ----- Title Search Tab -----
        titleLayout = QVBoxLayout()
        formLayout = QHBoxLayout()
        self.titleLabel = QLabel("Movie Title:")
        self.titleInput = QLineEdit()
        self.searchButton = QPushButton("Search")
        # This button triggers the genre-based search by title
        self.searchButton.clicked.connect(self.get_similar_movies_by_title)
        formLayout.addWidget(self.titleLabel)
        formLayout.addWidget(self.titleInput)
        formLayout.addWidget(self.searchButton)
        titleLayout.addLayout(formLayout)
        
        # Table to display title search results
        self.titleTable = QTableWidget()
        # Set 5 columns: the last for the See Overview button
        self.titleTable.setColumnCount(5)
        self.titleTable.setHorizontalHeaderLabels(["Title", "Release Date", "Genres", "Rating", "Actions"])
        titleLayout.addWidget(self.titleTable)
        self.tabTitleSearch.setLayout(titleLayout)

        # ----- Filter Search Tab -----
        filterLayout = QVBoxLayout()
        gridLayout = QGridLayout()
        
        # Genre filter
        gridLayout.addWidget(QLabel("Genre:"), 0, 0)
        self.genreCombo = QComboBox()
        self.genreCombo.addItems(["Any", "Action", "Comedy", "Drama", "Horror", "Romance"])
        gridLayout.addWidget(self.genreCombo, 0, 1)
        
        # Rating filter
        gridLayout.addWidget(QLabel("Minimum Rating:"), 1, 0)
        self.ratingCombo = QComboBox()
        self.ratingCombo.addItems(["Any", "5", "6", "7", "8", "9"])
        gridLayout.addWidget(self.ratingCombo, 1, 1)

        # Release period filter
        gridLayout.addWidget(QLabel("Release Period:"), 2, 0)
        self.periodCombo = QComboBox()
        self.periodCombo.addItems(["Any", "Pre 2000", "Post 2000"])
        gridLayout.addWidget(self.periodCombo, 2, 1)
        
        filterLayout.addLayout(gridLayout)
        self.filterSearchButton = QPushButton("Search")
        self.filterSearchButton.clicked.connect(self.get_movies_by_filters)
        filterLayout.addWidget(self.filterSearchButton)

        # Table for filtered results (again, 5 columns for Actions)
        self.filterTable = QTableWidget()
        self.filterTable.setColumnCount(5)
        self.filterTable.setHorizontalHeaderLabels(["Title", "Release Date", "Genres", "Rating", "Actions"])
        filterLayout.addWidget(self.filterTable)
        self.tabFilterSearch.setLayout(filterLayout)

        # ----- Main Layout -----
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.tabs)
        self.setLayout(mainLayout)

    def get_database_connection(self):
        """Establish and return a connection to the MySQL database."""
        try:
            connection = mysql.connector.connect(
                host='comp373.cianci.io',         # Update if needed
                user='kpapa',                  # Replace with your MySQL username
                password='firm-limited-eye', # Replace with your MySQL password
                database='comp373',
                port=3306 
            )
            return connection
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Connection Error", f"Error: {err}")
            return None

    def get_similar_movies_by_title(self):
        """Find a movie by title and then search for similar movies based on genre."""
        title = self.titleInput.text().strip()
        if not title:
            QMessageBox.warning(self, "Input Error", "Please enter a movie title.")
            return

        connection = self.get_database_connection()
        if connection is None:
            return
        cursor = connection.cursor(dictionary=True)
        try:
            # Search for the movie by title (limit to 1 result)
            query = "SELECT * FROM BC_KP_DatabaseProject WHERE title LIKE %s LIMIT 1"
            cursor.execute(query, ('%' + title + '%',))
            movie = cursor.fetchone()
            if not movie:
                QMessageBox.information(self, "No Results", "Movie not found!")
                return
            
            # Use the found movie's genres to search for similar movies
            genre = movie.get("genres", "")
            query_similar = """
                SELECT title, release_date, genres, vote_average, overview
                FROM BC_KP_DatabaseProject 
                WHERE genres LIKE %s 
                LIMIT 10
            """
            cursor.execute(query_similar, ('%' + genre + '%',))
            results = cursor.fetchall()
            self.populate_table(self.titleTable, results)
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Query Error", f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

    def get_movies_by_filters(self):
        """Search for movies based on selected filters."""
        genre = self.genreCombo.currentText()
        rating = self.ratingCombo.currentText()
        period = self.periodCombo.currentText()

        connection = self.get_database_connection()
        if connection is None:
            return
        cursor = connection.cursor(dictionary=True)
        try:
            # Corrected query: removed extra comma before FROM
            query = "SELECT title, release_date, genres, vote_average, overview FROM BC_KP_DatabaseProject WHERE 1=1"
            params = []
            if genre != "Any":
                query += " AND genres LIKE %s"
                params.append('%' + genre + '%')
            if rating != "Any":
                try:
                    rating_val = float(rating)
                    query += " AND vote_average >= %s"
                    params.append(rating_val)
                except ValueError:
                    pass
            if period != "Any":
                if period == "Post 2000":
                    query += " AND release_date >= '2000-01-01'"
                elif period == "Pre 2000":
                    query += " AND release_date < '2000-01-01'"
            query += " LIMIT 10"
            cursor.execute(query, params)
            results = cursor.fetchall()
            self.populate_table(self.filterTable, results)
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Query Error", f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

    def get_similar_movies_by_overview(self):
        """Find a movie by title and then search for similar movies based on the overview text."""
        title = self.titleInput.text().strip()
        if not title:
            QMessageBox.warning(self, "Input Error", "Please enter a movie title.")
            return

        # Get recommendations based on overview similarity using the title as the key.
        recommendations = get_similar_movies(title, self.df, self.tfidf_matrix, self.tfidf, top_n=10)
        if recommendations.empty:
            QMessageBox.information(self, "No Recommendations", "No similar movies found!")
        else:
            # Convert the recommendations DataFrame to a list of dictionaries and populate the table.
            self.populate_table(self.titleTable, recommendations.to_dict(orient="records"))

    def populate_table(self, table, results):
        """Populate the given QTableWidget with query results and add a See Overview button."""
        table.setRowCount(0)
        for row_data in results:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(row_data.get("title", ""))))
            table.setItem(row, 1, QTableWidgetItem(str(row_data.get("release_date", ""))))
            table.setItem(row, 2, QTableWidgetItem(str(row_data.get("genres", ""))))
            table.setItem(row, 3, QTableWidgetItem(str(row_data.get("vote_average", ""))))
            
            overview_text = str(row_data.get("overview", ""))
            btn_overview = QPushButton("See Overview")
            # Use a lambda with a default argument to capture overview_text
            btn_overview.clicked.connect(lambda _, text=overview_text: self.show_overview_popup(text))
            table.setCellWidget(row, 4, btn_overview)

    def show_overview_popup(self, overview):
        """Display the movie overview in a popup dialog."""
        QMessageBox.information(self, "Overview", overview if overview else "No overview available.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RecommenderWindow()
    window.show()
    sys.exit(app.exec())

from Backend.app.db.connection import execute_query


def get_countries():
    return execute_query("SELECT * FROM vendor.countries ORDER BY country_id ASC")
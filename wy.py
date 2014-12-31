import datetime
import docutils.core
import flask
import os
import os.path


class Data(object):
    """
    Data for the site.
    """

    def __init__(self, path):
        self.path = path

    def meetings(self):
        """
        List all meetings in reverse date order.
        """
        # Load all meeting files and extract date from filename.
        meetings = []
        for filename in os.listdir(self.path):
            if not filename.endswith(".txt"):
                continue
            meetings.append(self._meeting_from_file(filename))
        # Sort in reverse date order.
        meetings.sort(key=lambda m: m["date"], reverse=True)
        return meetings

    def meeting(self, date):
        """
        Get meeting for given date.
        """
        return self._meeting_from_file(date + ".txt")

    def _meeting_from_file(self, filename):
        """
        Load a meeting from disk.
        """
        with open(os.path.join(self.path, filename)) as f:
            rst = f.read()
        parts = docutils.core.publish_parts(rst, writer_name="html")
        return {
            "date": second_thursday(os.path.splitext(filename)[0]),
            "title": parts["title"],
            "body": parts["body"]
        }


# Create data accessor and Flask app
data = Data("./data")
app = flask.Flask(__name__)


@app.route("/")
def index():
    return render_meeting()


@app.route("/<date>")
def meeting(date):
    return render_meeting(date)


def render_meeting(date=None):
    # Load all meetings and pivot around today's date.
    meetings = pivot_meetings(data.meetings())
    # Decide what meeting to treat as the page's meeting.
    meeting = meetings["current"] if not date else data.meeting(date)
    return flask.render_template(
        "index.html",
        meeting=meeting,
        previous=meetings["previous"],
        future=meetings["future"]
    )


def pivot_meetings(meetings):
    """
    Pivot a list of meetings (in reverse date order) around today's date to
    organise into previous, current and future.
    """

    today = datetime.date.today()
    split = {"previous": [], "current": None, "future": []}
    for meeting in meetings:
        if today > meeting["date"]:
            split["previous"].append(meeting)
        else:
            split["future"].append(meeting)

    # Select best meeting to use as "current".
    if split["future"]:
        split["current"] = split["future"].pop()
    else:
        split["current"] = split["previous"].pop(0)

    # Reverse future meetings so they're in data order, i.e. moving away from
    # the pivot date.
    split["future"].reverse()

    return split


def second_thursday(year_month):
    year, month = map(int, year_month.split("-"))
    date = datetime.date(year, month, 1)
    count = 2
    while True:
        if date.weekday() == 3:
            count -= 1
            if not count:
                break
        date += datetime.timedelta(days=1)
    return date


if __name__ == "__main__":
    app.run(debug=True)

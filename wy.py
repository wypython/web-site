import datetime
import docutils.core
import errno
import flask
import httplib
import os
import os.path
import yaml


class DataError(Exception):
    def __init__(self, status, reason=None):
        self.status = status
        self.reason = reason if reason else httplib.responses[status]


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
            if not filename.endswith(".yaml"):
                continue
            meetings.append(self._meeting_from_file(filename))
        # Sort in reverse date order.
        meetings.sort(key=lambda m: m["date"], reverse=True)
        return meetings

    def meeting(self, date):
        """
        Get meeting for given date.
        """
        return self._meeting_from_file(date + ".yaml")

    def _meeting_from_file(self, filename):
        """
        Load a meeting from disk.
        """
        try:
            with open(os.path.join(self.path, filename)) as f:
                doc = yaml.safe_load(f)
        except IOError as e:
            raise DataError(404) if e.errno == errno.ENOENT else e
        parts = docutils.core.publish_parts(
            doc['body'],
            writer_name="html",
            settings_overrides={"initial_header_level": 3}
        )
        doc["body"] = parts["body"]
        return doc


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
    if not date:
        meeting = meetings["current"]
    else:
        try:
            meeting = data.meeting(date)
        except DataError as e:
            return e.reason, e.status
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
        split["current"] = split["future"][-1]
    else:
        split["current"] = split["previous"][0]

    # Reverse future meetings so they're in data order, i.e. moving away from
    # the pivot date.
    split["future"].reverse()

    return split


if __name__ == "__main__":
    app.run(debug=True)

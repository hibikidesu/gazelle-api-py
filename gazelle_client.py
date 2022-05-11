import pickle
import os

import requests
import appdirs

__VERSION__ = "1.0.1"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                     "AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/74.0.3729.169 Safari/537.36"


class GazelleClient:

    def __init__(self,
                 host: str,
                 username: str = None,
                 password: str = None,
                 *,
                 user_agent: str = DEFAULT_USER_AGENT):
        self.host: str = host
        self._user_agent = user_agent

        self._session = requests.Session()
        self._login(username, password)

    def _login(self, username: str = None, password: str = None, twofa: str = ""):
        config_dir = appdirs.user_config_dir("gazelle_api_py", False)
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)

        # Load cookies if already saved to file
        config_file = os.path.join(config_dir, "cookies")
        if os.path.exists(config_file):
            with open(config_file, "rb") as f:
                self._session.cookies.update(pickle.load(f))

            # Check if cookies are valid else relogin and store cookies again
            try:
                self.index()
                return
            except ValueError:
                pass

        if username is not None and password is not None:
            response = self._session.post(
                f"{self.host}/login.php",
                data={
                    "username": username,
                    "password": password,
                    "twofa": twofa,
                    "login": "Log+in"
                },
                headers={
                    "User-Agent": self._user_agent
                }
            )

            if "login.php" in response.url:
                raise ValueError("Invalid username/password, failed to login")

            with open(config_file, "wb") as f:
                pickle.dump(self._session.cookies, f)
        else:
            raise ValueError("Neither session or username and password was not provided.")

    def get(self, action: str, **kwargs) -> dict:
        special = kwargs.pop("special", {})

        params = {
            "action": action,
            **kwargs
        }

        params.update(special)

        response = self._session.get(
            f"{self.host}/ajax.php",
            params=params,
            headers={
                "User-Agent": self._user_agent
            }
        )

        if "login.php" in response.url:
            raise ValueError("Unable to make request, invalid session")

        response.raise_for_status()
        return response.json()

    def index(self, **kwargs) -> dict:
        """
        Gets index page of the API

        Returns:
            Dict containing basic index data for the current logged in user
        """
        return self.get("index", **kwargs)

    def user(self, user_id: int, **kwargs) -> dict:
        """
        Gets info for a specified User ID

        Args:
            user_id (int): User to lookup

        Returns:
            Dict containing user information if exists
        """
        return self.get("user", id=str(user_id), **kwargs)

    def inbox(self, page: int = 1, inbox_type: str = "inbox", **kwargs) -> dict:
        """
        Gets the current logged in user's message inbox

        Args:
            page (int): Page number to display
            inbox_type (str): Either inbox or sentbox

        Extra Args:
            sort (str): If specified as "unread", unread messages will come first
            search (str): Filter messages by search string
            searchtype (str): Either subject/message/user

        Returns:
            Dict containing user inbox messages
        """
        return self.get("inbox", page=str(page), type=inbox_type, **kwargs)

    def conversation(self, conversation_id: int, **kwargs) -> dict:
        """
        Gets a conversation from an inbox

        Args:
            conversation_id (int): ID of the conversation

        Returns:

        """
        return self.get("inbox", type="viewconv", id=str(conversation_id), **kwargs)

    def top10(self, top_type: str = "torrents", limit: int = 10, **kwargs) -> dict:
        """
        Gets top information for the site

        Args:
            top_type (str): Either torrents/tags/users
            limit (int): Amount of data to retrieve

        Returns:
            Dict containing top information for specified type and amount
        """
        return self.get("top10", type=top_type, limit=str(limit), **kwargs)

    def user_search(self, search: str, page: int = 1, **kwargs) -> dict:
        """
        Search for a user for specified string

        Args:
            search (str): Search terms to find a user by
            page (int): Page to search on

        Returns:
            Dict of found users from search term
        """
        return self.get("usersearch", search=search, page=str(page), **kwargs)

    def requests(self, page: int = 1, **kwargs) -> dict:
        """
        Search for requests

        Args:
            page (int): Page number to get results from

        Extra Args:
            search (str): Search terms
            tag (str): Comma seperated tags for a search result
            tags_type (str): 0 for any, 1 to match all
            show_filled (str): To include filled requests or not, either true/false as a string

        Returns:
            Dict containing found requests based on search results
        """
        return self.get("requests", page=str(page), **kwargs)

    def torrents(self, page: int = 1, **kwargs) -> dict:
        """
        Find torrents based on search terms for the site

        Args:
            page (int): Page number to get results from

        Extra Args, depends on the site:
            searchstr (str): Search terms to find torrents based on

        Returns:
            Dict containing torrent information found
        """
        return self.get("browse", page=str(page), **kwargs)

    def bookmarks(self, bookmark_type: str = "torrents", **kwargs) -> dict:
        """
        Get the current logged in user's bookmarks

        Args:
            bookmark_type (str): Either torrents/artists

        Returns:
            Dict containing data the user has bookmarked
        """
        return self.get("bookmarks", type=bookmark_type, **kwargs)

    def subscriptions(self, showunread: int = 1, **kwargs) -> dict:
        """
        Gets subscriptions for a user

        Args:
            showunread (int): 1 to show only unread, 0 for all subscriptions

        Returns:
            Dict containing the users subscription feed
        """
        return self.get("subscriptions", showunread=showunread, **kwargs)

    def forums(self, **kwargs) -> dict:
        """
        Get forums

        Returns:
            Forum data from specified type
        """
        return self.get("forum", type="main", **kwargs)

    def forum_view(self, forum_id: int, page: int = 1, **kwargs) -> dict:
        """
        Views a forum from given id

        Args:
            forum_id (int): Forum id to lookup
            page (int): Forum page

        Returns:
            Dict containing forum data to view
        """
        return self.get("forum", type="viewforum", forumid=str(forum_id), page=str(page), **kwargs)

    def thread_view(self, thread_id: int, page: int = 1, **kwargs) -> dict:
        """
        View a forum thread

        Args:
            thread_id (int): Thread ID to display
            page (int): Page of the thread

        Extra Args:
            postid (int): Response will be the page including the post with this id
            updatelastread (int): Set to 1 to not update the last read id

        Returns:
            Dict containing thread data
        """
        return self.get("forum", type="viewthread", threadid=str(thread_id), page=str(page), **kwargs)

    def artist(self, **kwargs) -> dict:
        """
        Get artist data from specified params

        Extra Args:
            id (int): Artist's ID
            artistname (str): Artist's name
            artistreleases (str): If set, only include groups where the artist is the main artist.

        Returns:
            Dict containing artist data
        """
        return self.get("artist", **kwargs)

    def torrent(self, **kwargs) -> dict:
        """
        Get a specific torrent

        Extra Args:
            id (int): ID of the torrent
            hash (str): Hash of the torrent

        Returns:
            Dict containing torrent data
        """
        return self.get("torrent", **kwargs)

    def torrent_group(self, **kwargs) -> dict:
        """
        Get the group of a torrent

        Extra Args:
            id (int): ID of the torrent group
            hash (str): Hash of the torrent group

        Returns:
            Dict containing torrent group data
        """
        return self.get("torrentgroup", **kwargs)

    def request(self, request_id: int, page: int = 1, **kwargs) -> dict:
        """
        Get a request based on its id

        Args:
            request_id (int): Request to get
            page (int): Page number for the request's comments

        Returns:
            Dict containing the data of a request
        """
        return self.get("request", id=str(request_id), page=str(page), **kwargs)

    def collages(self, collage_id: int, **kwargs) -> dict:
        """
        Gets a collage based on its id

        Args:
            collage_id (int): The collages ID to retrieve

        Returns:
            Dict containing collage data
        """
        return self.get("collage", id=str(collage_id), **kwargs)

    def notifications(self, page: int = 1, **kwargs) -> dict:
        """
        Gets notifications for the logged in user

        Args:
            page (int): Page to get notifications of

        Returns:
            Dict containing notification data for a user
        """
        return self.get("notifications", page=str(page), **kwargs)

    def similar_artists(self, artist_id: int, limit: int, **kwargs):
        """
        Get similar artists based on an artist

        Args:
            artist_id (int): The artists id to get similar artists from
            limit (int): Amount of similar artists to get

        Returns:
            Dict containing similar artists
        """
        return self.get("similar_artists", id=str(artist_id), limit=str(limit), **kwargs)

    def announcements(self, **kwargs) -> dict:
        """
        Get announcements for the site

        Returns:
            Dict containing announcement data
        """
        return self.get("announcements", **kwargs)

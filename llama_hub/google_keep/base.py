"""Google Keep reader."""

import os
from typing import Any, List

from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document

SCOPES = ["https://www.googleapis.com/auth/keep.readonly"]


# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class GoogleKeepReader(BaseReader):
    """Google Keep reader.

    Reads notes from Google Keep

    """

    def load_data(self, note_ids: List[str]) -> List[Document]:
        """Load data from the note_ids.

        Args:
            note_ids (List[str]): a list of note ids.
        """
        if note_ids is None:
            raise ValueError('Must specify a "note_ids" in `load_kwargs`.')

        results = []
        for note_id in note_ids:
            note = self._load_note(note_id)
            results.append(Document(text=note, extra_info={"note_id": note_id}))
        return results

    def _load_note(self, note_id: str) -> str:
        """Load a note from Google Keep.

        Args:
            note_id: the note id.

        Returns:
            The note text.
        """
        import googleapiclient.discovery as discovery

        credentials = self._get_credentials()
        notes_service = discovery.build("keep", "v1", credentials=credentials)
        note = notes_service.notes().get(name=f"notes/{note_id}").execute()
        note_content = 'Title: ' + note.get('title') + '\n'
        note_content += 'Body: ' + note.get("body").get("text")
        # TODO: support list content.
        return note_content

    def _get_credentials(self) -> Any:
        """Get valid user credentials from storage.

        The file service_account.json stores the service account credentials which should have
        domain-wide delegation access to the Google Keep API.

        Returns:
            Credentials, the obtained credential.
        """
        from google.oauth2 import service_account

        if os.path.exists("service_account.json"):
            creds = service_account.Credentials.from_service_account_file(
                "service_account.json", scopes=SCOPES
            )
            return creds
        # If there are no (valid) credentials available, notify the user.
        # Note Google Keep API currently only supports service accounts with
        # domain-wide delegation access.
        raise RuntimeError('Need to authenticate with service account.')


if __name__ == "__main__":
    reader = GoogleKeepReader()
    print(
        reader.load_data(note_ids=["1eKU7kGn8eJCErZ52OC7vCzHDSQaspFYGHHCiTX_IvhFOc7ZQZVJhTIDFMdTJOPiejOk"])
    )

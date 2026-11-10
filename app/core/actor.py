"""The logged-in user, as the services see it."""

from dataclasses import dataclass

ALL_FARMERS = "data.all_farmers"  # Privilege to see and change the data of all farmers


@dataclass(frozen=True)
class Actor:
    id: int
    username: str
    roles: frozenset[str]
    privileges: frozenset[str]

    def has(self, privilege: str) -> bool:
        return privilege in self.privileges

    @property
    def unrestricted(self) -> bool:  # False: the user sees only their own data and their assigned farmers
        return self.has(ALL_FARMERS)

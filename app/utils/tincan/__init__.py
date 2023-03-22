"""
Client library for communicating with an LRS (Learning Record Store)
implementing Tin Can API version 1.0.0 or 1.0.1.

Web site: <https://github.com/RusticiSoftware/TinCanPython>

For more info about the Tin Can API, see <http://tincanapi.com/>.
"""

# These imports are for convenience to external modules only.
# Internal tincan modules should continue to use explicit imports,
# since this file will not have run yet.
#
# For example, from the outside, you can say:
# from tincan import RemoteLRS, LRSResponse
#
# but inside the tincan package, we have to use:
#    from app.utils.tincan.remote_lrs import RemoteLRS
#    from app.utils.tincan.lrs_response import LRSResponse

from app.utils.tincan.about import About
from app.utils.tincan.activity import Activity
from app.utils.tincan.activity_definition import ActivityDefinition
from app.utils.tincan.activity_list import ActivityList
from app.utils.tincan.agent import Agent
from app.utils.tincan.agent_account import AgentAccount
from app.utils.tincan.agent_list import AgentList
from app.utils.tincan.attachment import Attachment
from app.utils.tincan.attachment_list import AttachmentList
from app.utils.tincan.base import Base
from app.utils.tincan.context import Context
from app.utils.tincan.context_activities import ContextActivities
from app.utils.tincan.documents.activity_profile_document import ActivityProfileDocument
from app.utils.tincan.documents.agent_profile_document import AgentProfileDocument
from app.utils.tincan.documents.document import Document
from app.utils.tincan.documents.state_document import StateDocument
from app.utils.tincan.extensions import Extensions
from app.utils.tincan.group import Group
from app.utils.tincan.http_request import HTTPRequest
from app.utils.tincan.interaction_component import InteractionComponent
from app.utils.tincan.interaction_component_list import InteractionComponentList
from app.utils.tincan.language_map import LanguageMap
from app.utils.tincan.lrs_response import LRSResponse
from app.utils.tincan.remote_lrs import RemoteLRS
from app.utils.tincan.result import Result
from app.utils.tincan.score import Score
from app.utils.tincan.serializable_base import SerializableBase
from app.utils.tincan.statement import Statement
from app.utils.tincan.statement_base import StatementBase
from app.utils.tincan.statement_list import StatementList
from app.utils.tincan.statement_ref import StatementRef
from app.utils.tincan.statement_targetable import StatementTargetable
from app.utils.tincan.statements_result import StatementsResult
from app.utils.tincan.substatement import SubStatement
from app.utils.tincan.typed_list import TypedList
from app.utils.tincan.verb import Verb
from app.utils.tincan.version import Version

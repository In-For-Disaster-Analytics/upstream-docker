from unittest.mock import patch
import pytest
from app.services.project_service import ProjectService
from app.pytas.models.schemas import PyTASUser, PyTASProject, PyTASPi, PyTASAllocation

# Mock data for testing
MOCK_PI_DATA = PyTASPi(
    id=1001,
    username="jdoe",
    email="john.doe@example.com",
    firstName="John",
    lastName="Doe",
    institution="Test University",
    institutionId=1,
    department="Computer Science",
    departmentId=1,
    citizenship="United States",
    citizenshipId=1,
    source="System",
    uid=10001,
    homeDirectory="/home/jdoe",
    gid=5000
)

MOCK_ALLOCATION_ACTIVE = PyTASAllocation(
    id=1,
    start="2024-01-01",
    end="2024-12-31",
    status="Active",
    justification="Research needs",
    decisionSummary="Approved",
    dateRequested="2023-12-01",
    dateReviewed="2023-12-15",
    computeRequested=100000,
    computeAllocated=100000,
    storageRequested=1000,
    storageAllocated=1000,
    memoryRequested=128,
    memoryAllocated=128,
    resourceId=1,
    resource="Frontera",
    projectId=123,
    project="Project Alpha",
    requestorId=1001,
    requestor="John Doe",
    reviewerId=2001,
    reviewer=None,
    computeUsed=50000.0
)

MOCK_ALLOCATION_INACTIVE = PyTASAllocation(
    id=2,
    start="2023-01-01",
    end="2023-12-31",
    status="Inactive",
    justification="Research needs",
    decisionSummary="Completed",
    dateRequested="2022-12-01",
    dateReviewed="2022-12-15",
    computeRequested=200000,
    computeAllocated=200000,
    storageRequested=2000,
    storageAllocated=2000,
    memoryRequested=256,
    memoryAllocated=256,
    resourceId=1,
    resource="Frontera",
    projectId=456,
    project="Project Beta",
    requestorId=1002,
    requestor="Jane Smith",
    reviewerId=2001,
    reviewer=None,
    computeUsed=180000.0
)

MOCK_PROJECT_DATA = [
    PyTASProject(
        id=123,
        title="Project Alpha",
        description="Research project for quantum computing",
        chargeCode="ABC-123",
        gid=5000,
        source=None,
        fieldId=1,
        field="Computer Science",
        typeId=1,
        type="Research",
        piId=1001,
        pi=MOCK_PI_DATA,
        allocations=[MOCK_ALLOCATION_ACTIVE],
        nickname=None
    ),
    PyTASProject(
        id=456,
        title="Project Beta",
        description="Climate modeling research",
        chargeCode="XYZ-456",
        gid=5001,
        source=None,
        fieldId=2,
        field="Environmental Science",
        typeId=1,
        type="Research",
        piId=1002,
        pi=MOCK_PI_DATA.model_copy(update={"id": 1002, "username": "jsmith"}),
        allocations=[MOCK_ALLOCATION_INACTIVE],
        nickname=None
    )
]

MOCK_PROJECT_MEMBERS = [
    PyTASUser(
        id=2001,
        username="testuser1",
        role="PI",
        firstName="Test",
        lastName="User1",
        email="test1@example.com"
    ),
    PyTASUser(
        id=2002,
        username="testuser2",
        role="Researcher",
        firstName="Test",
        lastName="User2",
        email="test2@example.com"
    )
]

@pytest.fixture
def project_service():
    with patch.dict('os.environ', {
        'tasURL': 'http://example.com',
        'tasUser': 'test_user',
        'tasSecret': 'test_password'
    }):
        return ProjectService()

@pytest.mark.parametrize("username", ["testuser"])
def test_get_projects_for_user(project_service, username):
    # Arrange
    test_user = username
    with patch.object(project_service.client, 'projects_for_user') as mock_projects:
        mock_projects.return_value = [proj.dict() for proj in MOCK_PROJECT_DATA]

        # Act
        result = project_service.get_projects_for_user(test_user)

        # Assert
        mock_projects.assert_called_once_with(username=test_user)
        assert len(result) == 1  # Only active projects should be returned

        active_project = result[0]
        assert active_project["id"] == 123
        assert active_project["title"] == "Project Alpha"
        assert active_project["chargeCode"] == "ABC-123"
        assert active_project["allocations"][0]["status"] == "Active"

        # Verify nested objects
        allocation = active_project["allocations"][0]
        assert allocation["computeRequested"] == 100000
        assert allocation["computeAllocated"] == 100000
        assert allocation["computeUsed"] == 50000.0

        pi = active_project["pi"]
        assert pi["username"] == "jdoe"
        assert pi["institution"] == "Test University"
        assert pi["department"] == "Computer Science"

def test_get_project_members(project_service):
    # Arrange
    project_id = "test_project"
    with patch.object(project_service.client, 'get_project_members') as mock_members:
        mock_members.return_value = [member.dict() for member in MOCK_PROJECT_MEMBERS]

        # Act
        result = project_service.get_project_members(project_id)

        # Assert
        mock_members.assert_called_once_with(project_id=project_id)
        assert len(result) == 2

        # Verify first member
        member1 = result[0]
        assert member1["username"] == "testuser1"
        assert member1["role"] == "PI"
        assert member1["firstName"] == "Test"
        assert member1["lastName"] == "User1"

        # Verify second member
        member2 = result[1]
        assert member2["username"] == "testuser2"
        assert member2["role"] == "Researcher"

def test_get_projects_for_user_no_active_projects(project_service):
    # Arrange
    test_user = "testuser"
    inactive_project = PyTASProject(
        id=789,
        title="Inactive Project",
        description="Inactive project description",
        chargeCode="INV-789",
        gid=5002,
        source=None,
        fieldId=1,
        field="Physics",
        typeId=1,
        type="Research",
        piId=1003,
        pi=MOCK_PI_DATA.model_copy(update={"id": 1003, "username": "inactive_pi"}),
        allocations=[MOCK_ALLOCATION_INACTIVE.model_copy(update={"id": 3})],
        nickname=None
    )

    with patch.object(project_service.client, 'projects_for_user') as mock_projects:
        mock_projects.return_value = [inactive_project.dict()]

        # Act
        result = project_service.get_projects_for_user(test_user)

        # Assert
        assert len(result) == 0  # Should return empty list when no active projects
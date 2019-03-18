from __future__ import absolute_import

from rest_framework.response import Response

from sentry.api import client
from sentry.api.base import DocSection
from sentry.api.bases.group import GroupEndpoint
from sentry.models import Group
from sentry.utils.apidocs import scenario, attach_scenarios


@scenario('GetLatestGroupSample')
def get_latest_group_sample_scenario(runner):
    project = runner.default_project
    group = Group.objects.filter(project=project).first()
    runner.request(
        method='GET',
        path='/issues/%s/events/latest/' % group.id,
    )


class GroupEventsLatestEndpoint(GroupEndpoint):
    doc_section = DocSection.EVENTS

    @attach_scenarios([get_latest_group_sample_scenario])
    def get(self, request, group):
        """
        Retrieve the Latest Event for an Issue
        ``````````````````````````````````````

        Retrieves the details of the latest event for an issue.

        :pparam string group_id: the ID of the issue
        """

        requested_environments = set(request.GET.getlist('environment'))

        event = group.get_latest_event_for_environments(requested_environments)

        if not event:
            return Response({'detail': 'No events found for group'}, status=404)

        try:
            return client.get(u'/projects/{}/{}/events/{}/'.format(
                event.organization.slug,
                event.project.slug,
                event.event_id
            ), request=request)
        except client.ApiError as e:
            return Response(e.body, status=e.status_code)

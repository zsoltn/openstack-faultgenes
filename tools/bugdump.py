import json
from launchpadlib.launchpad import Launchpad
import os


class BugDump(object):
    def __init__(self, debug=False, limit=False, count=5):
        self.limit = limit
        self.count = count  # Stop after N bugs if limit = True
        self.debug = debug
        if self.debug:
            print("Enabling debug output")
        if self.limit:
            print("Limiting report to %d bugs" % self.count)

    def meta_keys(self):
        keys = [
            'assignee_link',
            'bug_link',
            'bug_target_display_name',
            'bug_target_name',
            'date_created',
            'importance',
            'owner_link',
            'related_tasks_collection_link',
            'self_link',
            'status',
            'target_link',
            'title',
            'web_link'
        ]
        '''
        unused_keys = [
            'http_etag',
            'is_complete',
            'milestone_link',
            'resource_type_link',
            'bug_watch_link',
            'date_assigned',
            'date_closed',
            'date_confirmed',
            'date_fix_committed',
            'date_fix_released',
            'date_in_progress',
            'date_incomplete',
            'date_left_closed',
            'date_left_new',
            'date_triaged',
        ]
        '''
        return keys

    def report(self, project='neutron'):
        cachedir = os.path.join(os.environ['HOME'], 'Code/launchpad/cache')
        lp = Launchpad.login_anonymously('just testing', 'production',
                                         cachedir, version='devel')
        p = lp.projects[project]
        '''
        status = [
            'New', "Won't Fix", 'Incomplete', 'Opinion', 'Expired',
            'Confirmed', 'Triaged', 'Fix Committed', 'Fix Released',
            'Incomplete (with response)', 'Incomplete (without response)']
        '''
        # pass status to filter on a subset of bugs
        bug_tasks = p.searchTasks()
        table = {}
        meta_keys = self.meta_keys()
        print("Found %d bugs in project %s" % (len(bug_tasks), project))
        for task in bug_tasks:
            bug = lp.bugs.getBugData(bug_id=task.bug.id)[0]
            if self.debug:
                print("Found data for %s" % task)
            else:
                print '.',
            table[task.bug.id] = {}
            table[task.bug.id]['details'] = bug
            table[task.bug.id]['meta'] = {}
            for key in meta_keys:
                table[task.bug.id]['meta'][key] = getattr(task, key)
                if key == 'date_created':
                    # need to render this field as a string
                    table[task.bug.id]['meta'][key] = \
                        str(table[task.bug.id]['meta'][key])
            if self.limit:
                if self.count == 0:
                    break
                self.count -= 1
        print("\nFinished compiling table for project %s" % project)
        return table


if __name__ == "__main__":
    b = BugDump(debug=True, limit=True, count=5)
    bugs = b.report()
    with open('bugdump.json', 'w') as fp:
        json.dump(bugs, fp)

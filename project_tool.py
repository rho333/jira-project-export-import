import sys, os
from jira import JIRA, Comment
import yaml

def usage(error=None):
    if error:
        print(error)
    else:
        print("Malformed or missing arguments.")
    print("project_tool.py [import|export] <project_key> <source/dest file>")
    sys.exit(1)

try:
    operation = sys.argv[1].strip()
    project_key = sys.argv[2].strip()
    filename = sys.argv[3].strip()
except:
    usage()

try:
    with open('.jira_cfg', 'r') as credfile:
        creds = credfile.read()
    lines = creds.split("\n")
    server = lines[0].strip()
    username = lines[1].strip()
    password = lines[2].strip()
except:
    usage("Malformed or absent credentials/config file. Ensure .jira_cfg is present and has server, username and password on separate lines.")

jira_instance = JIRA(basic_auth=(username, password), options={'server': server})

if operation == "export":
    project_data = []
    issues = jira_instance.search_issues('project=%s' % project_key)
    if len(issues) == 0:
        usage("Provided project doesn't exist or has no issues to export.")
    for issue in issues:
        print("Exporting %s..." % issue.key)
        issue_dict = {
            'old_key': issue.key,
            'summary': issue.fields.summary,
            'reporter': {'name': issue.fields.reporter.name},
            'assignee': {'name': issue.fields.assignee.name} if issue.fields.assignee else None,
            'description': issue.fields.description,
            'priority': {'id': issue.fields.priority.id},
            'status': {'name': issue.fields.status.name},
            'issuetype': {'name': issue.fields.issuetype.name},
            'comments': None
        }

        comment_list = []
        comments = jira_instance.comments(issue)
        for comment in comments:
            comment_list.append({
                'body': comment.body,
                'author': comment.author.name,
                'created': comment.created
            })
        issue_dict['comments'] = comment_list

        project_data.append(issue_dict)
    with open(filename, 'w') as outfile:
        outfile.write(yaml.dump(project_data, default_flow_style=False))
elif operation == "import":
    with open(filename, 'r') as data_file:
        project_data = yaml.load(data_file)
    for issue_dict in project_data:
        old_key = issue_dict['old_key']
        comments = issue_dict['comments']
        del issue_dict['old_key']
        del issue_dict['comments']
        del issue_dict['status']
        
        issue_dict['project'] = project_key
        new_issue = jira_instance.create_issue(fields=issue_dict)
        print("%s is now %s" % (old_key, new_issue.key))

        for comment in comments:
            body = "Originally posted by [~%s] at/on %s:\n\n%s" % (comment['author'], comment['created'], comment['body'])
            jira_instance.add_comment(issue=new_issue, body=body)

JIRA API Project Import/Export Tool
===================================

This is a basic Python script that allows import and export of JIRA projects via the API. In effect, it:

1. Uses the JIRA API to retrieve all issues for a given project.
2. Writes the representation of these issues, and their comments to a YAML file.
3. (Import mode) Reads that YAML file.
4. Creates new issues in a target project, populating them with the details of each issue in the YAML file.

Limitations
-----------

The script is capable of accurately recreating the following field values (assuming the values are valid in the target JIRA instance):

* Reporter
* Assignee
* Summary
* Description
* Priority
* Issue Type

It **DOES NOT** import the following fields (which may be rather important to you):

* Status
* Comment author/original dates/times (original author is mentioned in the regenerated comments).
* Security Level
* Labels
* Components
* Any other fields not mentioned in the previous list!
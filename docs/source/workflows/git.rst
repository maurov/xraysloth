Personal Git-related notes
--------------------------

I do not use Git so often to remember all the steps (and commands) to
contribute to open-source projects (usually hosted on Github), so here I write
down some notes.

Howtos
''''''

- Add upstream tracking of a forked project::

    git remote add --track master upstream https://forked_project.git

- Fetch a specific branch from a source (here the case of `upstream`)::

    git remote -v  # shows all remote sources
    git fetch upstream remote_branch_name:local_brach_name

- Delete a branch::

    git branch --delete your_branch_name      # locally
    git push origin --delete your_branch_name # remotely

- `Pull from a given remote branch <https://stackoverflow.com/questions/1709177/git-pull-a-certain-branch-from-github>`_::

    git pull origin other-branch

- `Overwrite any local changes on pull <http://stackoverflow.com/questions/1125968/force-git-to-overwrite-local-files-on-pull>`_::

    git fetch --all
    git reset --hard origin/master

- `Clone all remote branches <http://stackoverflow.com/questions/67699/clone-all-remote-branches-with-git>`_::

    git clone git://example.com/myproject
    cd myproject
    git branch -a # to show all branches
    git checkout -b experimental origin/experimental  # creates a local tracking branch

- `Change Github authentification from HTTPS to SSH <https://stackoverflow.com/questions/2432764/how-to-change-the-uri-url-for-a-remote-git-repository>`_::

    #First add a public SSH key (e.g. `~/.ssh/id_rsa.pub`)
    git remote -v
    git remote set-url origin git@gihub.com:USERNAME/REPOSITORY.git
    git remote -v


Configuration
'''''''''''''

- Username and email::

    git config --global user.name "Your Name"
    git config --global user.email "your.email@your_provider.com"

- `Temporary cache password <https://stackoverflow.com/questions/5343068/is-there-a-way-to-skip-password-typing-when-using-https-on-github/5343146#5343146>`_ for one hour::

    git config --global credential.helper "cache --timeout=3600"

- Proxy (here at ESRF)::

    git config --global http.proxy http://proxy.esrf.fr:3128
    git config --global https.proxy https://proxy.esrf.fr:3128

Branching workflow
''''''''''''''''''

- Click `fork` button on the repo you want to contribute to.
- Clone it locally to your machine.
- Add upstream track for updates (here example on `pymca` repo)::

    git remote add --track master upstream git://github.com/vasole/pymca.git

- To fetch and merge updates from the master original project::

    git fetch upstream
    git merge upstream/master

- To show all remote repositories ('origin' is the forked one,
  'upstream' is the original project)::

    git remote -v

- Make a working branch and switch to it::

    git branch your_branch_name
    git checkout your_branch_name
    git branch -a #(this will show all the branches and put * on working one)

- If the working branch exists already remotely::

    git checkout your_remote_branch

- Push your local changes to a remote branch::

    git push origin your_branch_name

- Go to your fork's webpage on Github and click 'pull-request' button give
  pull-request a name, fill in details of what changes you made, click submit
  button.  you're done!!

- Once the pull request accepted/rejected you can delete your branch::

    git branch --delete your_branch_name      #locally
    git push origin --delete your_branch_name #remotely

Specific cases
''''''''''''''

- `Fetch a given remote branch <https://stackoverflow.com/questions/9537392/git-fetch-remote-branch>`_::

    git checkout --track origin/daves_branch
    # This is equivalent to
    git checkout -b [branch] [remotename]/[branch]

- Merge master into a feature branch (`well explained here <https://stackoverflow.com/questions/16955980/git-merge-master-into-feature-branch>`_, see also `gitflow <https://github.com/nvie/gitflow>`_)::

    # Case 1 (single commits of the feature branch will be added to master
    #        (NOTE: this will pollute the history with fragmented commits)
    git checkout feature1
    git merge master

    # Case 2: you do not want to have the commits from the bug fixes in your feature branch
    git checkout feature1
    git rebase master

    # Manage all conflicts that arise. When you get to the commits with the bugfixes
    # (already in master), git will say that there were no changes and that maybe they
    # were already applied. You then continue the rebase (while skipping the commits
    # already in master) with::

    git rebase --skip

- Useful links

    - `Tutorial at gun.io <https://gun.io/blog/how-to-github-fork-branch-and-pull-request/>`_
    - `Pull request made easy at StackOverflow <http://stackoverflow.com/questions/14680711/how-to-do-a-github-pull-request>`_
    - `Workflow without branch <http://www.pontikis.net/blog/how-to-collaborate-on-github-open-source-projects>`_
    - `Another collaborating workflow example <http://www.eqqon.com/index.php/Collaborative_Github_Workflow>`_

Tags
''''

`Basics explained here <https://git-scm.com/book/en/v2/Git-Basics-Tagging>`_

- New annotated tag::

    git tag -a v1.4 -m "my version 1.4"

- List existing tags and show details::

    git tag
    git show v1.4

- Push to remote server::

    git push origin v1.4

- Delete local tag::

    git tag -d tag_name

- Delete remote tag::

    git tag --delete origin tag_name


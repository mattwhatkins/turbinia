# Developing new Turbinia Tasks and Evidence types

## It's easy!
Creating new Tasks for Turbinia is fairly easy, and if your Task is simple (like
just executing an external command) it should only take a few lines of real
code along with a bit of boiler-plate code, and a few extra lines to connect
things together.

## Before you start
*   Check out the [How it Works](how-it-works.md) page to see how the different
    components work within Turbinia.
*   Make sure to follow the Turbinia [developer contribution
 guide](contributing.md).

## Task code
The Worker which runs the tasks handles the following things before you even get
to the `run()` method where most of our code will go:
*   Running any pre- or post-processors that need to run to prepare the
    Evidence.
*   If the Evidence is file-based, the pre-processor should make that path
    available as `evidence.local_path`.  Similarly, if the Task generates any
    new Evidence objects, you must set the `.local_path` attribute of that
    before you add it to the results.
*   Setting up a temporary directory (available as `self.output_dir`).
*   It prepares a TurbiniaResult object to save results into.

To see a relatively simple example of the code required for a new Task, see this
[pull request](https://github.com/google/turbinia/pull/207).  This simply
executes the strings binary on Disk-based Evidence types.

Here is the bulk of the actual Task code for the Ascii Strings Task:
```python
    # Create the new Evidence object that will be generated by this Task.
    output_evidence = TextFile()
    # Create a path that we can write the new file to.
    base_name = os.path.basename(evidence.local_path)
    output_file_path = os.path.join(
        self.output_dir, '{0:s}.ascii'.format(base_name))
    # Add the output path to the evidence so we can automatically save it
    # later.
    output_evidence.local_path = output_file_path

    # Generate the command we want to run.
    cmd = 'strings -a -t d {0:s} > {1:s}'.format(
        evidence.local_path, output_file_path)
    # Add a log line to the result that will be returned.
    result.log('Running strings as [{0:s}]'.format(cmd))
    # Actually execute the binary
    self.execute(
        cmd, result, new_evidence=[output_evidence], close=True, shell=True)
```

This is mostly self explanatory from the comments, but the line that needs a
little more explaining is this one:
```python
    self.execute(
        cmd, result, new_evidence=[output_evidence], close=True, shell=True)
```

This will:
*   Run the command as specified
*   Save the stdout and stderr in the results object specified

Also, because `close=True` is set in this call, it will finalze the results in
order to prepare them to be returned to to the Task Manager.  Closing a result
does a few things like set task stats, save all of the output files, and run the
post-processor to free up the Evidence (e.g. unmount disks, etc).  If you have
other external commands that you want to run and save the output from, you
should not close the results until after these are all complete (i.e. just don't
set `close=True`).  If you are not calling the `execute()` function and closing
the results that way, you'll need to close them similar to this:
```
result.close(self, success=True, status='My message about the Task status')
```

One important parameter that was not set in the call for `self.close()` is
`save_files`.  It takes a list of file paths that you want to save (no need to
add the files you linked to the Evidence earlier, it will save those
automatically).  This is used for non-Evidence files that you want to save (for
example log files).

If you want to write temporary files from your task, you should do this relative
to the self.output_dir.  This is a directory that is unique for this Task.

If you are not using the `self.execute()` method, then you will need to close
the result object before exiting.  

The `run()` function should return the result object and these will also be
serialized and returned to the server. The new Evidence created and included
in the results will be checked by the Task Manager to see if there are other
Tasks that should be scheduled to process it.

## Boilerplate and Glue
The only two interesting bits for the Job definition in
`turbinia/jobs/strings.py` are this one that sets the input and output evidence
types for the Task (so the Task Manager knows what kinds of Tasks to schedule):
```python
  evidence_input = [type(RawDisk()), type(GoogleCloudDisk()),
                    type(GoogleCloudDiskRawEmbedded())]
  evidence_output = [type(TextFile())]
```

And this one, which just sets up the Tasks for both Task types (Ascii and
Unicode):
```
    tasks = [StringsAsciiTask() for _ in evidence]
    tasks.extend([StringsUniTask() for _ in evidence])
    return tasks
```

In this case we have two separate tasks that we are executing for the Job, but
it's possible that there could be more or less depending on how much you want
to split it up.  Then you just need to add a reference to the new job in
`turbinia/jobs/__init__.py`.

## Notes
*   The reason we separate out the strings processing into two separate Tasks is
    so we can do them in parallel and save on wall-time.
*   One caveat about Task development is that it is possible to create a cycle
    in the Task Manager by generating Evidence types that your Task (or any of
    its parent's tasks) also listens to.  Check out the [Job and Evidence
    graph generator](https://github.com/google/turbinia/blob/master/tools/turbinia_job_graph.py)
    if you want to verify that there aren't any cycles in the graph.
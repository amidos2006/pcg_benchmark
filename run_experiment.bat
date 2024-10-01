@ECHO OFF

REM Call this script with `run_experiments.bat environment_name number_of_iterations number_of_runs`

FOR %%G IN (random, ga, es) DO (
    FOR %%F IN (quality, quality_control, quality_control_diversity) DO (
        FOR /L %%X IN (1,1,%3) DO (
            echo "%1 with %%G (fitness: %%F; run %%X / %3)"
            python run.py ./results/%1/%%F/%%G/%%X -p %1 -g %%G -s %2 --fitness %%F
        )
    )
)
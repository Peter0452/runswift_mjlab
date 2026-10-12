cmake_minimum_required(VERSION 3.8)
project(behaviour)

find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  find_package(ament_cmake_pytest REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
  ament_add_pytest_test(test_world_model test/test_world_model.py)
  ament_add_pytest_test(test_ball_tracker test/test_ball_tracker.py)
  ament_add_pytest_test(test_team_ball_fusion test/test_team_ball_fusion.py)
  ament_add_pytest_test(test_blocking test/test_blocking.py)
  ament_add_pytest_test(test_skills test/test_skills.py)
  ament_add_pytest_test(test_action_arbiter test/test_action_arbiter.py)
  ament_add_pytest_test(test_skill_calibration test/test_skill_calibration.py)
  # The legacy ROS environment may use Python 3.10. Enable only with the
  # standalone world-model package installed in the test interpreter (3.11+).
  option(BEHAVIOUR_WORLD_MODEL_TESTS "Test skills with the standalone world model" OFF)
  if(BEHAVIOUR_WORLD_MODEL_TESTS)
    ament_add_pytest_test(test_world_skills test/test_world_skills.py)
    ament_add_pytest_test(test_world_navigation test/test_world_navigation.py)
    ament_add_pytest_test(test_booster_navigation test/test_booster_navigation.py)
    ament_add_pytest_test(test_navigation_execution test/test_navigation_execution.py)
    ament_add_pytest_test(test_match_runner test/test_match_runner.py)
    ament_add_pytest_test(test_match_tactics test/test_match_tactics.py)
    ament_add_pytest_test(test_match_actuator test/test_match_actuator.py)
  endif()
endif()

# python scripts
install(
  PROGRAMS
  scripts/ball_chasing_wm_simplified.py
  scripts/blocking.py
  scripts/clear_target_provider.py
  scripts/simple_clear_target.py
  scripts/ball_physics.py
  scripts/ball_tracker.py
  scripts/team_ball_fusion.py
  scripts/object_avoidance_apf.py
  scripts/legacy_world_model.py
  scripts/runswift_types.py
  scripts/world_skills_demo.py
  scripts/match_runner.py
  scripts/match_tactics.py
  scripts/match_execution.py
  scripts/match_feedback.py
  scripts/world_match_replay.py

  scripts/navigation_planner.py
  scripts/navigation_execution.py
  scripts/navigation_safety.py
  scripts/navigation_types.py
  scripts/path_tracker.py
  scripts/se2_planner.py
  scripts/simplier_planner.py
    scripts/walk_to_pose_demo.py
    scripts/open_day_demo.py
    scripts/demo_kick_ball_action_no_perception.py
    scripts/demo_kick_ball_action_with_perception.py
    DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY scripts/action scripts/skills
  DESTINATION lib/${PROJECT_NAME}
  PATTERN "__pycache__" EXCLUDE
)

ament_package()

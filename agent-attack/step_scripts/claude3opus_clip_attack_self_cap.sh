python scripts/eval_step_attack.py \
  --attack clip_attack \
  --result_dir step_test_claude_som \
  --provider anthropic \
  --model claude-3-opus-20240229 \
  --temperature 0 \
  --action_set_tag som  --observation_type image_som

# Get the results
python scripts/report_metric.py \
  --result_file step_test_claude_som/target_correct_clip_attack_cap.json

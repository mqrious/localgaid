String durationSecondsToString(int durationSeconds) {
  final hours = durationSeconds ~/ 3600;
  final minutes = (durationSeconds % 3600) ~/ 60;
  final secs = durationSeconds % 60;

  final hh = hours.toString().padLeft(2, '0');
  final mm = minutes.toString().padLeft(2, '0');
  final ss = secs.toString().padLeft(2, '0');

  if (hours == 0) {
    return '$mm:$ss';
  }

  return '$hh:$mm:$ss';
}

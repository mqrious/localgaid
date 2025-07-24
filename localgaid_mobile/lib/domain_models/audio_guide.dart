import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:localgaid_mobile/utils.dart';

part 'audio_guide.freezed.dart';
part 'audio_guide.g.dart';

@freezed
abstract class AudioGuide with _$AudioGuide {
  const AudioGuide._();

  const factory AudioGuide({
    required int id,
    required int placeId,
    required String title,
    required int durationSeconds,
    required String audioUrl,
    required String subtitleUrl,
    String? fullSubtitle,
  }) = _AudioGuide;

  factory AudioGuide.fromJson(Map<String, Object?> json) =>
      _$AudioGuideFromJson(json);

  String get duration {
    return durationSecondsToString(durationSeconds);
  }
}

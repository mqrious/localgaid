// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'audio_guide.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_AudioGuide _$AudioGuideFromJson(Map<String, dynamic> json) => _AudioGuide(
  id: (json['id'] as num).toInt(),
  placeId: (json['place_id'] as num).toInt(),
  title: json['title'] as String,
  durationSeconds: (json['duration_seconds'] as num).toInt(),
  audioUrl: json['audio_url'] as String,
  subtitleUrl: json['subtitle_url'] as String,
  fullSubtitle: json['full_subtitle'] as String?,
);

Map<String, dynamic> _$AudioGuideToJson(_AudioGuide instance) =>
    <String, dynamic>{
      'id': instance.id,
      'place_id': instance.placeId,
      'title': instance.title,
      'duration_seconds': instance.durationSeconds,
      'audio_url': instance.audioUrl,
      'subtitle_url': instance.subtitleUrl,
      'full_subtitle': instance.fullSubtitle,
    };

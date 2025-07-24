// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'audio_guide.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$AudioGuide {

 int get id; int get placeId; String get title; int get durationSeconds; String get audioUrl; String get subtitleUrl; String? get fullSubtitle;
/// Create a copy of AudioGuide
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AudioGuideCopyWith<AudioGuide> get copyWith => _$AudioGuideCopyWithImpl<AudioGuide>(this as AudioGuide, _$identity);

  /// Serializes this AudioGuide to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AudioGuide&&(identical(other.id, id) || other.id == id)&&(identical(other.placeId, placeId) || other.placeId == placeId)&&(identical(other.title, title) || other.title == title)&&(identical(other.durationSeconds, durationSeconds) || other.durationSeconds == durationSeconds)&&(identical(other.audioUrl, audioUrl) || other.audioUrl == audioUrl)&&(identical(other.subtitleUrl, subtitleUrl) || other.subtitleUrl == subtitleUrl)&&(identical(other.fullSubtitle, fullSubtitle) || other.fullSubtitle == fullSubtitle));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,placeId,title,durationSeconds,audioUrl,subtitleUrl,fullSubtitle);

@override
String toString() {
  return 'AudioGuide(id: $id, placeId: $placeId, title: $title, durationSeconds: $durationSeconds, audioUrl: $audioUrl, subtitleUrl: $subtitleUrl, fullSubtitle: $fullSubtitle)';
}


}

/// @nodoc
abstract mixin class $AudioGuideCopyWith<$Res>  {
  factory $AudioGuideCopyWith(AudioGuide value, $Res Function(AudioGuide) _then) = _$AudioGuideCopyWithImpl;
@useResult
$Res call({
 int id, int placeId, String title, int durationSeconds, String audioUrl, String subtitleUrl, String? fullSubtitle
});




}
/// @nodoc
class _$AudioGuideCopyWithImpl<$Res>
    implements $AudioGuideCopyWith<$Res> {
  _$AudioGuideCopyWithImpl(this._self, this._then);

  final AudioGuide _self;
  final $Res Function(AudioGuide) _then;

/// Create a copy of AudioGuide
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? placeId = null,Object? title = null,Object? durationSeconds = null,Object? audioUrl = null,Object? subtitleUrl = null,Object? fullSubtitle = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,placeId: null == placeId ? _self.placeId : placeId // ignore: cast_nullable_to_non_nullable
as int,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,durationSeconds: null == durationSeconds ? _self.durationSeconds : durationSeconds // ignore: cast_nullable_to_non_nullable
as int,audioUrl: null == audioUrl ? _self.audioUrl : audioUrl // ignore: cast_nullable_to_non_nullable
as String,subtitleUrl: null == subtitleUrl ? _self.subtitleUrl : subtitleUrl // ignore: cast_nullable_to_non_nullable
as String,fullSubtitle: freezed == fullSubtitle ? _self.fullSubtitle : fullSubtitle // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _AudioGuide extends AudioGuide {
  const _AudioGuide({required this.id, required this.placeId, required this.title, required this.durationSeconds, required this.audioUrl, required this.subtitleUrl, this.fullSubtitle}): super._();
  factory _AudioGuide.fromJson(Map<String, dynamic> json) => _$AudioGuideFromJson(json);

@override final  int id;
@override final  int placeId;
@override final  String title;
@override final  int durationSeconds;
@override final  String audioUrl;
@override final  String subtitleUrl;
@override final  String? fullSubtitle;

/// Create a copy of AudioGuide
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AudioGuideCopyWith<_AudioGuide> get copyWith => __$AudioGuideCopyWithImpl<_AudioGuide>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AudioGuideToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _AudioGuide&&(identical(other.id, id) || other.id == id)&&(identical(other.placeId, placeId) || other.placeId == placeId)&&(identical(other.title, title) || other.title == title)&&(identical(other.durationSeconds, durationSeconds) || other.durationSeconds == durationSeconds)&&(identical(other.audioUrl, audioUrl) || other.audioUrl == audioUrl)&&(identical(other.subtitleUrl, subtitleUrl) || other.subtitleUrl == subtitleUrl)&&(identical(other.fullSubtitle, fullSubtitle) || other.fullSubtitle == fullSubtitle));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,placeId,title,durationSeconds,audioUrl,subtitleUrl,fullSubtitle);

@override
String toString() {
  return 'AudioGuide(id: $id, placeId: $placeId, title: $title, durationSeconds: $durationSeconds, audioUrl: $audioUrl, subtitleUrl: $subtitleUrl, fullSubtitle: $fullSubtitle)';
}


}

/// @nodoc
abstract mixin class _$AudioGuideCopyWith<$Res> implements $AudioGuideCopyWith<$Res> {
  factory _$AudioGuideCopyWith(_AudioGuide value, $Res Function(_AudioGuide) _then) = __$AudioGuideCopyWithImpl;
@override @useResult
$Res call({
 int id, int placeId, String title, int durationSeconds, String audioUrl, String subtitleUrl, String? fullSubtitle
});




}
/// @nodoc
class __$AudioGuideCopyWithImpl<$Res>
    implements _$AudioGuideCopyWith<$Res> {
  __$AudioGuideCopyWithImpl(this._self, this._then);

  final _AudioGuide _self;
  final $Res Function(_AudioGuide) _then;

/// Create a copy of AudioGuide
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? placeId = null,Object? title = null,Object? durationSeconds = null,Object? audioUrl = null,Object? subtitleUrl = null,Object? fullSubtitle = freezed,}) {
  return _then(_AudioGuide(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,placeId: null == placeId ? _self.placeId : placeId // ignore: cast_nullable_to_non_nullable
as int,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,durationSeconds: null == durationSeconds ? _self.durationSeconds : durationSeconds // ignore: cast_nullable_to_non_nullable
as int,audioUrl: null == audioUrl ? _self.audioUrl : audioUrl // ignore: cast_nullable_to_non_nullable
as String,subtitleUrl: null == subtitleUrl ? _self.subtitleUrl : subtitleUrl // ignore: cast_nullable_to_non_nullable
as String,fullSubtitle: freezed == fullSubtitle ? _self.fullSubtitle : fullSubtitle // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on

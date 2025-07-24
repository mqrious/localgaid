import 'package:localgaid_mobile/domain_models/audio_guide.dart';
import 'package:localgaid_mobile/domain_models/place.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

abstract class PlaceRepository {
  Future<List<Place>> fetchPlaces() async {
    throw UnimplementedError();
  }

  Future<(Place, List<AudioGuide>)> getPlace({required int id}) async {
    throw UnimplementedError();
  }
}

class PlaceRepositoryImpl implements PlaceRepository {
  SupabaseClient supabaseClient;

  PlaceRepositoryImpl({required this.supabaseClient});

  @override
  Future<List<Place>> fetchPlaces() async {
    final data = (await supabaseClient.rpc('fetch_places')) as List<dynamic>;

    List<Place> places = data.map((json) => Place.fromJson(json)).toList();
    return places;
  }

  @override
  Future<(Place, List<AudioGuide>)> getPlace({required int id}) async {
    final placeData = await supabaseClient
        .from('places')
        .select('id, name, images')
        .eq('id', id)
        .single();
    Place place = Place.fromJson(placeData);

    final audioGuideData = await supabaseClient
        .from('audio_guides')
        .select()
        .eq('place_id', id);
    List<AudioGuide> audioGuides = audioGuideData
        .map((json) => AudioGuide.fromJson(json))
        .toList();

    return (place, audioGuides);
  }
}

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:localgaid_mobile/components/place_card.dart';
import 'package:localgaid_mobile/domain_models/place.dart';
import 'package:localgaid_mobile/repositories/place_repository.dart';

class PlacesScreen extends StatefulWidget {
  final PlaceRepository placeRepository;

  const PlacesScreen({super.key, required this.placeRepository});

  @override
  State<PlacesScreen> createState() => _PlacesScreenState();
}

class _PlacesScreenState extends State<PlacesScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: EdgeInsetsGeometry.all(8),
        child: FutureBuilder<List<Place>>(
          future: widget.placeRepository.fetchPlaces(),
          builder: (BuildContext context, AsyncSnapshot<List<Place>> snapshot) {
            Widget child;
            if (snapshot.hasData) {
              child = ListView.separated(
                itemBuilder: (BuildContext context, int index) {
                  return PlaceCard(
                    place: snapshot.data![index],
                    onTap: (placeId) {
                      context.push('/places/$placeId');
                    },
                  );
                },
                separatorBuilder: (BuildContext context, int index) =>
                    const SizedBox(height: 8),
                itemCount: snapshot.data!.length,
              );
            } else if (snapshot.hasError) {
              child = const Icon(
                Icons.error_outline,
                color: Colors.red,
                size: 60,
              );
            } else {
              child = SizedBox(
                width: 60,
                height: 60,
                child: CircularProgressIndicator(),
              );
            }
            return Center(child: child);
          },
        ),
      ),
    );
  }
}
